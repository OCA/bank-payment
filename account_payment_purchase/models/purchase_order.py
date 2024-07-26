# Copyright 2016 Akretion (<http://www.akretion.com>).
# Copyright 2017 Tecnativa - Vicent Cubells.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    supplier_partner_bank_id = fields.Many2one(
        comodel_name="res.partner.bank",
        compute="_compute_supplier_partner_bank",
        readonly=False,
        store=True,
        precompute=True,
        string="Supplier Bank Account",
        domain="[('partner_id', 'parent_of', partner_id),"
        "('company_id', 'in', [False, company_id])]",
        check_company=True,
        help="Select the bank account of your supplier on which your company "
        "should send the payment. This field is copied from the partner "
        "and will be copied to the supplier invoice.",
    )
    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        compute="_compute_payment_mode",
        readonly=False,
        store=True,
        precompute=True,
        string="Payment Mode",
        domain="[('payment_type', '=', 'outbound'), ('company_id', '=', company_id)]",
        check_company=True,
    )

    @api.model
    def _get_default_supplier_partner_bank(self, partner):
        """This function is designed to be inherited"""
        return (
            partner.bank_ids
            and partner.bank_ids.sorted(lambda bank: not bank.allow_out_payment)[0].id
            or False
        )

    @api.depends("partner_id", "company_id")
    def _compute_payment_mode(self):
        for order in self:
            if order.partner_id:
                order = order.with_company(order.company_id)
                order.payment_mode_id = order.partner_id.supplier_payment_mode_id

    @api.depends("partner_id", "company_id", "payment_mode_id")
    def _compute_supplier_partner_bank(self):
        for order in self:
            if (
                order.payment_mode_id.payment_method_id.bank_account_required
                and order.partner_id
            ):
                order = order.with_company(order.company_id)
                order.supplier_partner_bank_id = (
                    order._get_default_supplier_partner_bank(order.partner_id)
                )
            elif not order.payment_mode_id.payment_method_id.bank_account_required:
                order.supplier_partner_bank_id = False

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res["payment_mode_id"] = self.payment_mode_id.id
        res.pop("partner_bank_id", False)
        if self.payment_mode_id.payment_method_id.bank_account_required:
            res["partner_bank_id"] = self.supplier_partner_bank_id.id
        return res
