from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def partner_banks_to_show(self):
        self.ensure_one()
        if self.payment_mode_id.payment_method_id.code == "sepa_direct_debit":
            return (
                self.mandate_id.partner_bank_id
                or self.partner_id.valid_mandate_id.partner_bank_id
            )
        return super().partner_banks_to_show()
