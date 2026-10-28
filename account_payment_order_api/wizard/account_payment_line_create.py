# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

from ..models.account_payment_api_line import RELEASED_STATES


class AccountPaymentLineCreate(models.TransientModel):
    _inherit = "account.payment.line.create"

    def _prepare_move_line_domain(self):
        """Propose again the journal items whose only open payment lines were
        refused, rejected, cancelled or returned by the bank, without waiting
        for the order to close."""
        domain = super()._prepare_move_line_domain()
        released = self.env["account.payment.api.line"].search(
            [("state", "in", RELEASED_STATES), ("move_line_id", "!=", False)]
        )
        if not released:
            return domain
        active_paylines = self.env["account.payment.line"].search(
            [
                ("state", "in", ("draft", "open", "generated")),
                ("move_line_id", "in", released.move_line_id.ids),
            ]
        )
        free = set(released.move_line_id.ids)
        for payline in active_paylines - released.payment_line_id:
            free.discard(payline.move_line_id.id)
        new_domain = []
        for leaf in domain:
            if isinstance(leaf, (list, tuple)) and tuple(leaf[:2]) == ("id", "not in"):
                leaf = ("id", "not in", [i for i in leaf[2] if i not in free])
            new_domain.append(leaf)
        return new_domain
