# Copyright 2016 Akretion (<http://www.akretion.com>).
# Copyright 2017 Tecnativa - Vicent Cubells.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("purchase_vendor_bill_id", "purchase_id")
    def _onchange_purchase_auto_complete(self):
        old_mode = self.payment_mode_id.id
        old_bank = self.partner_bank_id.id
        purchase_id = self.purchase_vendor_bill_id.purchase_order_id or self.purchase_id
        if purchase_id:
            new_invoice_vals = purchase_id.with_company(
                purchase_id.company_id
            )._prepare_invoice()
            new_mode = new_invoice_vals.get("payment_mode_id", False)
            new_bank = new_invoice_vals.get("partner_bank_id", False)
        else:
            new_mode = new_bank = False

        res = super()._onchange_purchase_auto_complete() or {}
        if old_mode and new_mode and old_mode != new_mode:
            res["warning"] = {
                "title": _("Warning"),
                "message": _("Selected purchase order have different payment mode."),
            }
            return res
        elif new_mode and self.payment_mode_id.id != new_mode:
            self.payment_mode_id = new_mode
        if old_bank and new_bank and old_bank != new_bank:
            res["warning"] = {
                "title": _("Warning"),
                "message": _("Selected purchase order have different supplier bank."),
            }
        elif new_bank and self.partner_bank_id.id != new_bank:
            self.partner_bank_id = new_bank
        return res
