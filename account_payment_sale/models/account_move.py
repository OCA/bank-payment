# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals_list):
        if vals_list.get("payment_mode_id"):
            payment_mode = self.env["account.payment.mode"].browse(
                vals_list["payment_mode_id"]
            )
            if payment_mode.bank_account_link == "fixed":
                vals_list[
                    "invoice_partner_bank_id"
                ] = payment_mode.fixed_journal_id.bank_account_id.id
        return super().create(vals_list)
