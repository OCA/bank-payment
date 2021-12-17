# Copyright 2014-2020 Akretion - Alexis de Lattre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        compute="_compute_payment_mode",
        store=True,
        readonly=False,
        check_company=True,
        domain="[('payment_type', '=', 'inbound'), ('company_id', '=', company_id)]",
    )

    @api.depends("partner_id")
    def _compute_payment_mode(self):
        for order in self:
            if order.partner_id:
                order.payment_mode_id = order.partner_id.customer_payment_mode_id
            else:
                order.payment_mode_id = False

    def _get_payment_mode_vals(self, vals):
        if self.payment_mode_id:
            vals["payment_mode_id"] = self.payment_mode_id.id
            if (
                self.payment_mode_id.bank_account_link == "fixed"
                and self.payment_mode_id.payment_method_id.code == "manual"
            ):
                vals[
                    "partner_bank_id"
                ] = self.payment_mode_id.fixed_journal_id.bank_account_id.id

    def _prepare_invoice(self):
        """Copy bank partner from sale order to invoice"""
        vals = super()._prepare_invoice()
        self._get_payment_mode_vals(vals)
        return vals
