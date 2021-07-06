# Copyright (C) 2021, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoicePaymentLineMulti(models.TransientModel):
    _inherit = "account.invoice.payment.line.multi"

    draft_orders = fields.Boolean(string="is Draft Payments available")
    info_message = fields.Html(string="Info")
    is_pyo_as_per_customer = fields.Boolean(string="As Per Customer", default=True)

    @api.model
    def default_get(self, field_list):
        res = super(AccountInvoicePaymentLineMulti, self).default_get(field_list)
        account_payment_order_obj = self.env["account.payment.order"]
        account_payment_order = account_payment_order_obj.search(
            [("state", "=", "draft")]
        )
        if not account_payment_order:
            res.update({"draft_orders": True})
        invoices = self.env["account.move"].browse(self._context["active_ids"])
        for invoice in invoices:
            no_draft_account_payment_order = account_payment_order_obj.search(
                [("partner_id", "=", invoice.partner_id.id), ("state", "=", "draft")]
            )
            if not no_draft_account_payment_order:
                res.update(
                    {
                        "info_message": """<p style='color:red'>This Partner has
                        no draft Invoice. </p>"""
                    }
                )
        return res

    def create_new_orders(self):
        self.ensure_one()
        assert (
            self._context["active_model"] == "account.move"
        ), "Active model should be account.move"
        invoices = self.env["account.move"].browse(self._context["active_ids"])
        action = invoices.with_context(
            is_pyo_as_per_customer=self.is_pyo_as_per_customer
        ).create_account_payment_line_new()
        self.env[action.get("res_model")].search([("state", "=", "new")]).write(
            {"state": "draft"}
        )
        return action

    def run(self):
        self.ensure_one()
        return super(
            AccountInvoicePaymentLineMulti,
            self.with_context(is_pyo_as_per_customer=self.is_pyo_as_per_customer),
        ).run()
