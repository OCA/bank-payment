# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.multi
    def make_po(self):
        res = super(ProcurementOrder, self).make_po()
        if self.purchase_id:
            if self.purchase_id.partner_id.supplier_payment_mode_id.id \
                and self.purchase_id.partner_id\
                    .supplier_payment_mode_id.purchase_ok:
                self.purchase_id.payment_mode_id = \
                    self.purchase_id.partner_id.supplier_payment_mode_id.id
            self.purchase_id.supplier_partner_bank_id = \
                self.purchase_id.partner_id.bank_ids \
                and self.purchase_id.partner_id.bank_ids[0].id or False
        return res

    @api.model
    def create_procurement_purchase_order(self, procurement, po_vals,
                                          line_vals):
        """Propagate payment mode on MTO/drop shipping."""
        if po_vals.get('partner_id'):
            partner = self.env['res.partner'].browse(po_vals['partner_id'])
            po_vals['payment_mode_id'] = partner.with_context(
                force_company=procurement.company_id.id).\
                supplier_payment_mode.id
            po_vals['supplier_partner_bank_id'] = (
                self.env['purchase.order']._get_default_supplier_partner_bank(
                    partner))
        return super(ProcurementOrder, self).create_procurement_purchase_order(
            procurement, po_vals, line_vals)
