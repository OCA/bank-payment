# Copyright 2015 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_purchase_order(self, company_id, origins, values):
        """Propagate payment mode on MTO/drop shipping."""
        res = super()._prepare_purchase_order(company_id, origins, values)
        values = values[0]
        partner = values["supplier"].partner_id
        if partner:
            res["payment_mode_id"] = partner.with_company(
                self.company_id.id
            ).supplier_payment_mode_id.id
            res["supplier_partner_bank_id"] = self.env[
                "purchase.order"
            ]._get_default_supplier_partner_bank(partner)
        return res
