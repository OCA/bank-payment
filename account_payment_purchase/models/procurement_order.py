# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.multi
    def _prepare_purchase_order(self, partner):
        """Propagate payment mode on MTO/drop shipping."""
        values = super(ProcurementOrder, self)._prepare_purchase_order(partner)
        if partner:
            values['payment_mode_id'] = partner.with_context(
                force_company=self.company_id.id).supplier_payment_mode_id.id
            values['supplier_partner_bank_id'] = (
                self.env['purchase.order']._get_default_supplier_partner_bank(
                    partner))
        return values
