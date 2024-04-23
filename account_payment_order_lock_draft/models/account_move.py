# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# flake8: noqa: B950

from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):

    _inherit = "account.move"

    def button_draft(self):
        """Handles the action of resetting entries to draft status.

        Performs the operation of resetting entries to draft status. It iterates
        through each entry, verifies if any associated payment order, and raises a UserError if so, preventing the reset operation.

        Raises:
            UserError: If an entry is associated with a Payment Order
        """
        super().button_draft()
        for move in self:
            if (
                self.env["account.move"]
                .sudo()
                .browse(move.id)
                .line_ids.filtered(lambda line: line.payment_line_ids)
            ):
                raise UserError(
                    _(
                        "You can't reset to draft because it's already associated with a Payment Order."
                    )
                )
