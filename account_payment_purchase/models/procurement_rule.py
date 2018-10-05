# Copyright 2015 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class ProcurementRule(models.Model):
    _inherit = "procurement.rule"

    def _prepare_purchase_order(self, product_id, product_qty, product_uom,
                                origin, values, partner):
        """Propagate payment mode on MTO/drop shipping."""
        values = super(ProcurementRule, self)._prepare_purchase_order(
            product_id, product_qty, product_uom, origin, values, partner)
        if partner:
            values['payment_mode_id'] = partner.with_context(
                force_company=self.company_id.id).supplier_payment_mode_id.id
            values['supplier_partner_bank_id'] = (
                self.env['purchase.order']._get_default_supplier_partner_bank(
                    partner))
        return values
