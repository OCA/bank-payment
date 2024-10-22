# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests.common import SavepointCase


class TestAccountInternalTransfer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountInternalTransfer, cls).setUpClass()

        cls.account_obj = cls.env["account.account"]
        cls.journal_obj = cls.env["account.journal"]
        cls.bank_obj = cls.env["res.partner.bank"]
        cls.internal_transfer_obj = cls.env["account.internal.transfer"]

        cls.company = cls.env.company

        cls.account_payable = cls.account_obj.create(
            {
                "code": "acc_payable",
                "name": "account payable",
                "reconcile": True,
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "company_id": cls.company.id,
            }
        )
        cls.account_receivable = cls.account_obj.create(
            {
                "code": "acc_receivable",
                "name": "account receivable",
                "reconcile": True,
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "company_id": cls.company.id,
            }
        )

        cls.company.transfer_payable_account_id = cls.account_payable
        cls.company.transfer_receivable_account_id = cls.account_receivable

        cls.transfer_journal = cls.journal_obj.create(
            {
                "name": "Transfer Journal",
                "code": "TRANS",
                "type": "general",
                "company_id": cls.company.id,
            }
        )
        cls.bank_account_1 = cls.bank_obj.create(
            {
                "acc_number": "101101-1",
                "company_id": cls.company.id,
                "partner_id": cls.company.partner_id.id,
            }
        )
        cls.bank_account_2 = cls.bank_obj.create(
            {
                "acc_number": "102201-2",
                "company_id": cls.company.id,
                "partner_id": cls.company.partner_id.id,
            }
        )
        cls.bank_journal_1 = cls.journal_obj.create(
            {
                "name": "TEST BANK",
                "code": "BANK",
                "type": "bank",
                "bank_account_id": cls.bank_account_1.id,
                "company_id": cls.company.id,
            }
        )
        cls.bank_journal_2 = cls.journal_obj.create(
            {
                "name": "TEST BANK 2",
                "code": "BANK2",
                "type": "bank",
                "bank_account_id": cls.bank_account_2.id,
                "company_id": cls.company.id,
            }
        )

        cls.date = datetime.now()
        cls.internal_transfer = cls.internal_transfer_obj.create(
            {
                "transfer_journal_id": cls.transfer_journal.id,
                "outgoing_journal_id": cls.bank_journal_1.id,
                "destination_journal_id": cls.bank_journal_2.id,
                "amount": 1000.0,
                "date": cls.date,
                "date_maturity": cls.date,
            }
        )

    def test_create_internal_transfer(self):
        move_id = self.internal_transfer.move_id
        credit_line = move_id.line_ids.filtered(lambda x: x.credit > 0)
        debit_line = move_id.line_ids.filtered(lambda x: x.debit > 0)

        self.assertEqual(move_id.date, datetime.date(self.date))
        self.assertEqual(move_id.journal_id, self.transfer_journal)

        self.assertEqual(debit_line.name, "Transfer from " + self.bank_journal_1.name)
        self.assertEqual(debit_line.account_id, self.account_receivable)
        self.assertEqual(debit_line.partner_id, self.company.partner_id)
        self.assertEqual(debit_line.debit, 1000.0)
        self.assertEqual(debit_line.date_maturity, datetime.date(self.date))
        self.assertEqual(debit_line.partner_bank_id, self.bank_account_1)

        self.assertEqual(credit_line.name, "Transfer to " + self.bank_journal_2.name)
        self.assertEqual(credit_line.account_id, self.account_payable)
        self.assertEqual(credit_line.partner_id, self.company.partner_id)
        self.assertEqual(credit_line.credit, 1000.0)
        self.assertEqual(credit_line.date_maturity, datetime.date(self.date))
        self.assertEqual(credit_line.partner_bank_id, self.bank_account_2)

    def test_write_internal_transfer(self):
        move_id = self.internal_transfer.move_id
        credit_line = move_id.line_ids.filtered(lambda x: x.credit > 0)
        debit_line = move_id.line_ids.filtered(lambda x: x.debit > 0)

        self.internal_transfer.write(
            {
                "outgoing_journal_id": self.bank_journal_2.id,
                "destination_journal_id": self.bank_journal_1.id,
                "amount": 1200.0,
            }
        )

        self.assertEqual(debit_line.name, "Transfer from " + self.bank_journal_2.name)
        self.assertEqual(debit_line.debit, 1200.0)
        self.assertEqual(debit_line.partner_bank_id, self.bank_account_2)

        self.assertEqual(credit_line.name, "Transfer to " + self.bank_journal_1.name)
        self.assertEqual(credit_line.credit, 1200.0)
        self.assertEqual(credit_line.partner_bank_id, self.bank_account_1)

    def test_action_confirm(self):
        move_id = self.internal_transfer.move_id
        self.internal_transfer.action_confirm()
        self.assertEqual(move_id.state, "posted")
        self.assertEqual(self.internal_transfer.state, "posted")

    def test_action_cancel(self):
        move_id = self.internal_transfer.move_id
        self.internal_transfer.action_cancel()
        self.assertEqual(move_id.state, "cancel")
        self.assertEqual(self.internal_transfer.state, "cancel")

    def test_action_draft(self):
        move_id = self.internal_transfer.move_id
        self.internal_transfer.action_draft()
        self.assertEqual(move_id.state, "draft")
        self.assertEqual(self.internal_transfer.state, "draft")
