import requests
from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request


class PlaidOnboardController(http.Controller):
    @http.route(
        ["/bank/connect/<string:token>"], auth="public", website=True, sitemap=False
    )
    def plaid_connect_page(self, token, **kwargs):
        partner = (
            request.env["res.partner"]
            .sudo()
            .search([("plaid_token", "=", token)], limit=1)
        )
        if not partner:
            raise NotFound()
        return request.render(
            "account_payment_plaid.portal_plaid_onboard",
            {
                "partner": partner,
            },
        )

    @http.route(
        "/payment/plaid/get_vendor_link_token",
        type="json",
        auth="public",
        methods=["POST"],
        cors="*",
        csrf=False,
    )
    def get_vendor_link_token(self, partner_id=None):
        if not partner_id:
            return {"error": "partner_id is required."}

        partner = request.env["res.partner"].sudo().browse(partner_id)
        if not partner.exists():
            return {"error": "Invalid partner_id."}

        company_id = request.env.company
        plaid_client_id = company_id.plaid_client_id
        plaid_secret = company_id.plaid_secret
        plaid_host = company_id.plaid_host

        if not plaid_client_id or not plaid_secret or not plaid_host:
            return {"error": "Invalid Plaid credentials"}

        interface = request.env["plaid.interface"]

        plaid_url = interface._get_host(plaid_host)

        if not plaid_url:
            return {"error": "Invalid Plaid environment"}

        payload = {
            "client_id": plaid_client_id,
            "secret": plaid_secret,
            "user": {"client_user_id": f"partner_{partner.id}"},
            "client_name": "Odoo Vendor Payments",
            "products": ["auth", "transfer"],
            "country_codes": ["US"],
            "language": "en",
        }

        try:
            r = requests.post(
                f"{plaid_url}/link/token/create", json=payload, timeout=10
            )
            data = r.json()
            if r.status_code != 200 or "link_token" not in data:
                return {
                    "error": data.get("error_message", "Error generating link_token")
                }
            return {"link_token": data["link_token"]}
        except Exception as e:
            return {"error": f"Error requesting link_token from Plaid: {str(e)}"}

    @http.route("/my/plaid/exchange_token", type="json", auth="public", csrf=False)
    def exchange_token(self, partner_id, public_token, account_ids):
        partner = request.env["res.partner"].sudo().browse(partner_id)
        if not partner:
            return {"error": "Invalid partner"}

        company_id = request.env.company
        plaid_client_id = company_id.plaid_client_id
        plaid_secret = company_id.plaid_secret
        plaid_host = company_id.plaid_host

        if not plaid_client_id or not plaid_secret or not plaid_host:
            return {"error": "Invalid Plaid credentials"}

        interface = request.env["plaid.interface"]
        plaid_url = interface._get_host(plaid_host)

        if not plaid_url:
            return {"error": "Invalid Plaid environment"}

        try:
            exchange_payload = {
                "client_id": plaid_client_id,
                "secret": plaid_secret,
                "public_token": public_token,
            }
            exchange_res = requests.post(
                f"{plaid_url}/item/public_token/exchange",
                json=exchange_payload,
                timeout=10,
            )
            exchange_data = exchange_res.json()
            access_token = exchange_data.get("access_token")
            if not access_token:
                return {"error": exchange_data.get("error_message", "Exchange failed")}

            auth_res = requests.post(
                f"{plaid_url}/auth/get",
                json={
                    "client_id": plaid_client_id,
                    "secret": plaid_secret,
                    "access_token": access_token,
                },
                timeout=10,
            )
            auth_data = auth_res.json()

            plaid_accounts = auth_data.get("accounts", [])
            plaid_numbers = auth_data.get("numbers", {}).get("ach", [])

            numbers_map = {item["account_id"]: item for item in plaid_numbers}

            saved_ids = []
            for acc in plaid_accounts:
                if acc["account_id"] not in account_ids:
                    continue

                number_info = numbers_map.get(acc["account_id"])
                if not number_info:
                    continue

                bank_name = (
                    acc.get("official_name") or acc.get("name") or "Unknown Bank"
                )
                bank_obj = (
                    request.env["res.bank"]
                    .sudo()
                    .search([("name", "=", bank_name)], limit=1)
                )
                if not bank_obj:
                    bank_obj = (
                        request.env["res.bank"].sudo().create({"name": bank_name})
                    )

                bank = (
                    request.env["res.partner.bank"]
                    .sudo()
                    .create(
                        {
                            "partner_id": partner.id,
                            "acc_number": number_info.get("account", ""),
                            "plaid_access_token": access_token,
                            "bank_id": bank_obj.id,
                            "acc_holder_name": acc.get("name"),
                            "plaid_account_id": acc["account_id"],
                            "plaid_subtype": acc.get("subtype"),
                            "plaid_routing_number": number_info.get("routing", ""),
                        }
                    )
                )
                saved_ids.append(bank.id)

            return {"status": "success", "stored_bank_ids": saved_ids}

        except Exception as e:
            return {"error": str(e)}

    @http.route("/bank/connect/success", type="http", auth="public", website=True)
    def plaid_connect_success(self):
        return request.render("account_payment_plaid.portal_plaid_success")
