# Copyright 2016 Akretion (<http://www.akretion.com>).
# Copyright 2017 Tecnativa - Vicent Cubells.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    supplier_partner_bank_id = fields.Many2one(
        comodel_name="res.partner.bank",
        string="Supplier Bank Account",
        domain="[('partner_id', '=', partner_id)]",
        help="Select the bank account of your supplier on which your company "
        "should send the payment. This field is copied from the partner "
        "and will be copied to the supplier invoice.",
    )
    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        string="Payment Mode",
        domain="[('payment_type', '=', 'outbound')]",
    )

    @api.model
    def _get_default_supplier_partner_bank(self, partner):
        """This function is designed to be inherited"""
        return partner.bank_ids and partner.bank_ids[0].id or False

    @api.onchange("partner_id", "company_id")
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        if self.partner_id:
            self = self.with_company(self.company_id)
            self.supplier_partner_bank_id = self._get_default_supplier_partner_bank(
                self.partner_id
            )
            self.payment_mode_id = self.with_company(
                self.company_id
            ).partner_id.supplier_payment_mode_id
        else:
            self.supplier_partner_bank_id = False
            self.payment_mode_id = False
        return res

    def _prepare_invoice(self):
        """Leave the bank account empty so that account_payment_partner set the
        correct value with compute."""
        invoice_vals = super()._prepare_invoice()
        invoice_vals.pop("partner_bank_id")
        return invoice_vals
