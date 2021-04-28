# Copyright 2016 Akretion (<http://www.akretion.com>).
# Copyright 2017 Tecnativa - Vicent Cubells.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("purchase_vendor_bill_id", "purchase_id")
    def _onchange_purchase_auto_complete(self):
        new_mode = self.purchase_id.payment_mode_id.id or False
        new_bank = self.purchase_id.supplier_partner_bank_id.id or False
        res = super()._onchange_purchase_auto_complete() or {}
        if self.payment_mode_id and new_mode and self.payment_mode_id.id != new_mode:
            res["warning"] = {
                "title": _("Warning"),
                "message": _("Selected purchase order have different payment mode."),
            }
            return res
        self.payment_mode_id = new_mode
        if self.partner_bank_id and new_bank and self.partner_bank_id.id != new_bank:
            res["warning"] = {
                "title": _("Warning"),
                "message": _("Selected purchase order have different supplier bank."),
            }
            return res
        self.partner_bank_id = new_bank
        return res
