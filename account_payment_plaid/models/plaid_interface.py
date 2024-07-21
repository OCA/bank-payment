# Copyright 2024 Binhex - Adasat Torres de León.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
try:
    import plaid
    from plaid.api import plaid_api
    from plaid.model.accounts_get_request import AccountsGetRequest
    from plaid.model.ach_class import ACHClass
    from plaid.model.country_code import CountryCode
    from plaid.model.item_public_token_exchange_request import (
        ItemPublicTokenExchangeRequest,
    )
    from plaid.model.link_token_create_request import LinkTokenCreateRequest
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
    from plaid.model.products import Products
    from plaid.model.sandbox_transfer_simulate_request import (
        SandboxTransferSimulateRequest,
    )
    from plaid.model.transfer_authorization_create_request import (
        TransferAuthorizationCreateRequest,
    )
    from plaid.model.transfer_authorization_user_in_request import (
        TransferAuthorizationUserInRequest,
    )
    from plaid.model.transfer_create_request import TransferCreateRequest
    from plaid.model.transfer_event_sync_request import TransferEventSyncRequest
    from plaid.model.transfer_failure import TransferFailure
    from plaid.model.transfer_network import TransferNetwork
    from plaid.model.transfer_type import TransferType


except (ImportError, IOError) as err:
    _logger.debug(err)


class PlaidInterface(models.AbstractModel):
    _name = "plaid.interface"
    _description = "Plaid Interface"

    def _get_host(self, host):
        if host == "sand":
            return plaid.Environment.Sandbox
        if host == "prod":
            return plaid.Environment.Production
        return False

    def _client(self, client_id, secret, host):
        configuration = plaid.Configuration(
            host=self._get_host(host),
            api_key={
                "clientId": client_id or "",
                "secret": secret or "",
            },
        )
        try:
            return plaid_api.PlaidApi(plaid.ApiClient(configuration))
        except plaid.ApiException as e:
            raise ValidationError(_("Error getting client api: %s") % e.body) from e

    def _link(self, client, language, country_code, company_name, products):
        request = LinkTokenCreateRequest(
            products=[Products(product) for product in products],
            client_name=company_name,
            country_codes=[CountryCode(country_code)],
            language=language,
            user=LinkTokenCreateRequestUser(client_user_id="client"),
        )
        try:
            response = client.link_token_create(request)
        except plaid.ApiException as e:
            raise ValidationError(_("Error getting link token: %s") % e.body) from e
        return response.to_dict()["link_token"]

    def _login(self, client, public_token):
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        try:
            response = client.item_public_token_exchange(request)
        except plaid.ApiException as e:
            raise ValidationError(_("Error getting access token: %s") % e.body) from e
        return response["access_token"]

    def _get_accounts(self, client, access_token):
        request = AccountsGetRequest(access_token=access_token)
        try:
            response = client.accounts_get(request)
        except plaid.ApiException as e:
            raise ValidationError(_("Error getting accounts: %s") % e.body) from e
        return response.to_dict()["accounts"]

    def _transfer_auth(self, client, access_token, account_id, partner_id, amount):
        request = TransferAuthorizationCreateRequest(
            access_token=access_token,
            account_id=account_id,
            originator_client_id=partner_id.plaid_client_id,
            type=TransferType("credit"),
            amount=amount,
            network=TransferNetwork("ach"),
            user=TransferAuthorizationUserInRequest(legal_name=partner_id.name),
            ach_class=ACHClass("ppd"),
        )

        try:
            response = client.transfer_authorization_create(request)
        except plaid.ApiException as e:
            raise ValidationError(_("Error getting transfer auth: %s") % e.body) from e
        response_dict = response.to_dict()["authorization"]
        return {
            "authorization_id": response_dict["id"],
            "decision": response_dict["decision"],
            "decision_rationale": response_dict["decision_rationale"],
        }

    def _transfer(
        self, client, access_token, account_id, authorization_id, description
    ):
        request = TransferCreateRequest(
            access_token=access_token,
            account_id=account_id,
            authorization_id=authorization_id,
            description=description,
        )
        try:
            response = client.transfer_create(request)
        except plaid.ApiException as e:
            raise ValidationError(_("Error creating transfer: %s") % e.body) from e
        return response.to_dict()["transfer"]

    def _sync_transfer_events(self, client):
        request = TransferEventSyncRequest(after_id=0, count=25)
        events = []
        try:
            response = client.transfer_event_sync(request)
            events.extend(response.to_dict()["transfer_events"])
        except plaid.ApiException as e:
            raise ValidationError(
                _("Error syncing transfer events: %s") % e.body
            ) from e

        has_more = response.to_dict().get("has_more", False)
        while has_more:
            request = TransferEventSyncRequest(after_id=len(events), count=25)
            try:
                response = client.transfer_event_sync(request)
                has_more = response.to_dict().get("has_more", False)
            except plaid.ApiException as e:
                raise ValidationError(
                    _("Error syncing transfer events: %s") % e.body
                ) from e
            events.extend(response.to_dict()["transfer_events"])
        return events

    ############################
    # Sandbox Transfer Methods #
    ############################

    def _sandbox_simulate_transfer(self, client, transfer_id, event_type, failure):
        if event_type == "failed":
            request = SandboxTransferSimulateRequest(
                transfer_id=transfer_id,
                event_type=event_type,
                failure_reason=TransferFailure(
                    description=failure,
                ),
            )
        else:
            request = SandboxTransferSimulateRequest(
                transfer_id=transfer_id,
                event_type=event_type,
            )

        try:
            client.sandbox_transfer_simulate(request)
        except plaid.ApiException as e:
            raise ValidationError(_("Error simulating transfer: %s") % e.body) from e

    def _sandbox_transfer_ledger_simulate_available(self, client):
        try:
            client.sandbox_transfer_ledger_simulate_available({})
        except plaid.ApiException as e:
            raise ValidationError(_("Error simulating transfer: %s") % e.body) from e
