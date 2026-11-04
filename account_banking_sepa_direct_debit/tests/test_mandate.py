# Copyright 2016-2020 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError

from .common import AccountBankingMandateCommon


class TestMandate(AccountBankingMandateCommon):
    def test_01_recurring_sequence_is_required(self):
        with self.assertRaises(UserError):
            self.mandate.recurrent_sequence_type = False
            self.mandate.type = "recurrent"
            self.mandate._check_recurring_type()

    def test_02_onchange_bank_resets_sequence(self):
        self.mandate.write(
            {"type": "recurrent", "recurrent_sequence_type": "recurring"}
        )
        self.mandate.validate()
        self.mandate.partner_bank_id = self.bank_account_02
        self.mandate.mandate_partner_bank_change()
        self.assertEqual(self.mandate.recurrent_sequence_type, "first")

    def test_03_expire_after_36_months(self):
        self.mandate.signature_date = fields.Date.today() + relativedelta(months=-35)
        self.mandate.validate()
        self.assertEqual(self.mandate.state, "valid")
        self.env["account.banking.mandate"]._sdd_mandate_set_state_to_expired()
        self.assertEqual(self.mandate.state, "valid")
        self.mandate.signature_date = fields.Date.today() + relativedelta(
            months=-36, days=-1
        )
        self.env["account.banking.mandate"]._sdd_mandate_set_state_to_expired()
        self.assertEqual(self.mandate.state, "expired")

    def test_04_email_does_not_activate_mandate(self):
        email_ctx = self.mandate.action_mandate_send().get("context", {})
        mail_template = (
            self.env["mail.template"]
            .sudo()
            .browse(email_ctx.get("default_template_id"))
            .copy({"auto_delete": False})
        )
        self.mandate.with_context(**email_ctx).message_post_with_source(mail_template)
        mail_message = self.mandate.message_ids[0]
        self.assertEqual(
            self.mandate.partner_id, mail_message.sudo().mail_ids.recipient_ids
        )
        self.assertEqual(self.mandate.state, "draft")
        self.assertTrue(self.mandate.is_sent)
