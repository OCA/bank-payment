# Copyright 2016-2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _default_outbound_payment_methods(self):
        all_out = self.env["account.payment.method"].search(
            [("payment_type", "=", "outbound")]
        )
        return all_out

    def _default_inbound_payment_methods(self):
        all_in = self.env["account.payment.method"].search(
            [("payment_type", "=", "inbound")]
        )
        return all_in

    outbound_payment_method_ids = fields.Many2many(
        default=_default_outbound_payment_methods
    )
    inbound_payment_method_ids = fields.Many2many(
        default=_default_inbound_payment_methods
    )

    @api.constrains("company_id")
    def company_id_account_payment_mode_constrains(self):
        for journal in self:
            mode = self.env["account.payment.mode"].search(
                [
                    ("fixed_journal_id", "=", journal.id),
                    ("company_id", "!=", journal.company_id.id),
                ],
                limit=1,
            )
            if mode:
                raise ValidationError(
                    _(
                        "The company of the journal '%s' does not match "
                        "with the company of the payment mode '%s' where it is "
                        "being used as Fixed Bank Journal."
                    )
                    % (journal.name, mode.name)
                )
            mode = self.env["account.payment.mode"].search(
                [
                    ("variable_journal_ids", "in", [journal.id]),
                    ("company_id", "!=", journal.company_id.id),
                ],
                limit=1,
            )
            if mode:
                raise ValidationError(
                    _(
                        "The company of the journal '%s' does not match "
                        "with the company of the payment mode '%s' where it is "
                        "being used in the Allowed Bank Journals."
                    )
                    % (journal.name, mode.name)
                )
