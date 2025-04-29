# Copyright 2014-2022 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commercial_invoice_partner_id = fields.Many2one(
        related="partner_invoice_id.commercial_partner_id",
        string="Invoicing Commercial Entity",
        store=True,
    )
    mandate_id = fields.Many2one(
        "account.banking.mandate",
        compute="_compute_mandate_id",
        string="Direct Debit Mandate",
        ondelete="restrict",
        check_company=True,
        readonly=False,
        store=True,
        tracking=True,
        domain="[('partner_id', '=', commercial_invoice_partner_id), "
        "('state', 'in', ('draft', 'valid')), "
        "('company_id', '=', company_id)]",
    )
    mandate_required = fields.Boolean(
        related="payment_mode_id.payment_method_id.mandate_required",
    )

    def _prepare_invoice(self):
        """Copy mandate from sale order to invoice"""
        vals = super()._prepare_invoice()
        if self.mandate_id:
            vals["mandate_id"] = self.mandate_id.id
        return vals

    @api.depends("partner_invoice_id", "payment_mode_id")
    def _compute_mandate_id(self):
        for order in self:
            if (
                order.partner_invoice_id
                and order.payment_mode_id
                and order.payment_mode_id.payment_method_id.mandate_required
            ):
                mandate = self.env["account.banking.mandate"].search(
                    [
                        ("state", "=", "valid"),
                        (
                            "partner_id",
                            "=",
                            order.partner_invoice_id.commercial_partner_id.id,
                        ),
                        ("company_id", "=", order.company_id.id),
                    ],
                    limit=1,
                )
                order.mandate_id = mandate or False
            else:
                order.mandate_id = False
