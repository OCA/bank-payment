from odoo import _, models


class AccountMove(models.Model):

    _inherit = "account.move"

    def action_payment_with_plaid_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Payment with Plaid"),
            "res_model": "account.payment.plaid.wizard",
            "view_mode": "form",
            "view_type": "form",
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_account_move_id": self.id,
                "default_amount": self.amount_total,
                "default_currency_id": self.currency_id.id,
                "default_description": self.name,
                "default_company_id": self.company_id.id,
            },
            "target": "new",
        }
