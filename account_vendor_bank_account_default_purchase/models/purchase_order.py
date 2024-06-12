# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _get_default_supplier_partner_bank(self, partner):
        if not partner.has_default_bank_id:
            return False
        elif partner.default_bank_id:
            return partner.default_bank_id.id
        else:
            return super()._get_default_supplier_partner_bank(partner)

    @api.depends("partner_id", "company_id")
    def _compute_payment_mode(self):
        res = super()._compute_payment_mode()
        for order in self:
            if (
                order.payment_mode_id.payment_method_id.bank_account_required
                and order.partner_id
            ):
                order.supplier_partner_bank_id = (
                    order._get_default_supplier_partner_bank(order.partner_id)
                )
            else:
                order.supplier_partner_bank_id = False
        return res
