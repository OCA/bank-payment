# Copyright 2016-2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import config


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _default_outbound_payment_methods(self):
        all_out = self.env["account.payment.method"].search(
            [("payment_type", "=", "outbound")]
        )
        return all_out

    def _default_inbound_payment_methods(self):
        method_info = self.env[
            "account.payment.method"
        ]._get_payment_method_information()
        unique_codes = tuple(
            code for code, info in method_info.items() if info.get("mode") == "unique"
        )
        all_in = self.env["account.payment.method"].search(
            [
                ("payment_type", "=", "inbound"),
                ("code", "not in", unique_codes),  # filter out unique codes
            ]
        )
        # 'electronic' are linked to a single journal per company per provider.
        electronic_codes = [
            code
            for code, info in method_info.items()
            if info.get("mode") == "electronic"
        ]
        if config["test_enable"]:
            # This is a hack to be able to test the electronic payment methods,
            # as they are defined when you install the account_payment module,
            # but the restrictions on electronic codes live in the account module.
            test_code = self.env.context.get("electronic_code", False)
            if test_code:
                electronic_codes.append(test_code)
        electronic_codes = tuple(electronic_codes)
        electronic_methods = self.env["account.payment.method"].search(
            [
                ("payment_type", "=", "inbound"),
                ("code", "in", electronic_codes),  # filter out unique codes
            ]
        )
        electronic_method_lines_already_assigned = self.env[
            "account.payment.method.line"
        ].search(
            [
                ("payment_method_id", "in", electronic_methods.ids),
                ("journal_id.company_id", "=", self.company_id.id),
                ("journal_id", "!=", self.id),
            ]
        )
        electronic_methods_already_assigned = (
            electronic_method_lines_already_assigned.mapped("payment_method_id")
        )
        res = all_in - electronic_methods_already_assigned
        return res

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
                        "The company of the journal %(journal)s does not match "
                        "with the company of the payment mode %(paymode)s where it is "
                        "being used as Fixed Bank Journal.",
                        journal=journal.name,
                        paymode=mode.name,
                    )
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
                        "The company of the journal  %(journal)s does not match "
                        "with the company of the payment mode  %(paymode)s where it is "
                        "being used in the Allowed Bank Journals.",
                        journal=journal.name,
                        paymode=mode.name,
                    )
                )
