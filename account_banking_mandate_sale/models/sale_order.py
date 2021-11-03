# Copyright 2014-2020 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # This field commercial_partner_id should be moved
    # in an OCA base module named for example sale_commercial_partner
    mandate_id = fields.Many2one(
        "account.banking.mandate",
        string="Direct Debit Mandate",
        ondelete="restrict",
        check_company=True,
        readonly=False,
        domain="[('partner_id', '=', commercial_partner_id), "
        "('state', 'in', ('draft', 'valid')), "
        "('company_id', '=', company_id)]",
    )
    mandate_required = fields.Boolean(
        related="payment_mode_id.payment_method_id.mandate_required",
    )

    def _prepare_invoice(self):
        """Copy mandate from sale order to invoice"""
        vals = super()._prepare_invoice()
        vals["mandate_id"] = self.mandate_id.id or False
        return vals

    @api.depends("partner_id")
    def _compute_payment_mode(self):
        """Select by default the first valid mandate of the partner"""
        super()._compute_payment_mode()
        abm_obj = self.env["account.banking.mandate"]
        for order in self:
            if order.mandate_required and order.partner_id:
                mandate = abm_obj.search(
                    [
                        ("state", "=", "valid"),
                        ("partner_id", "=", order.commercial_partner_id.id),
                        ("company_id", "=", order.company_id.id),
                    ],
                    limit=1,
                )
                order.mandate_id = mandate or False
            else:
                order.mandate_id = False
