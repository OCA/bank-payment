# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import Form, SavepointCase


class TestAccountMove(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.move_model = cls.env["account.move"]
        cls.journal_model = cls.env["account.journal"]
        cls.payment_term_model = cls.env["account.payment.term"]
        cls.payment_mode_model = cls.env["account.payment.mode"]
        cls.company = cls.env.ref("base.main_company")
        cls.journal_bank = cls.journal_model.create(
            {
                "name": "Test Bank Journal",
                "code": "TEST-BANK",
                "type": "bank",
                "company_id": cls.company.id,
                "bank_acc_number": "123456",
            }
        )
        cls.journal_sale = cls.env["account.journal"].create(
            {
                "name": "Test Sales Journal",
                "code": "tSAL",
                "type": "sale",
                "company_id": cls.company.id,
            }
        )
        cls.manual_in = cls.env.ref("account.account_payment_method_manual_in")
        cls.payment_term_a = cls.payment_term_model.create(
            {"name": "Test payment term A"}
        )
        cls.payment_term_b = cls.payment_term_model.create(
            {"name": "Test payment term B"}
        )
        cls.payment_mode_a = cls.payment_mode_model.create(
            {
                "name": "Test payment mode A",
                "bank_account_link": "fixed",
                "payment_method_id": cls.manual_in.id,
                "payment_type": "inbound",
                "company_id": cls.company.id,
                "fixed_journal_id": cls.journal_bank.id,
                "variable_journal_ids": [(6, 0, [cls.journal_bank.id])],
                "payment_term_ids": [(6, 0, [cls.payment_term_a.id])],
            }
        )
        cls.payment_mode_b = cls.payment_mode_model.create(
            {
                "name": "Test payment mode B",
                "bank_account_link": "fixed",
                "payment_method_id": cls.manual_in.id,
                "payment_type": "inbound",
                "company_id": cls.company.id,
                "fixed_journal_id": cls.journal_bank.id,
                "variable_journal_ids": [(6, 0, [cls.journal_bank.id])],
                "payment_term_ids": [(6, 0, [cls.payment_term_b.id])],
            }
        )

    def test_payment_mode_filter_invoices_term_a(self):
        move_form = Form(
            self.env["account.move"].with_context(
                default_type="out_invoice", company_id=self.company.id
            ),
        )
        move_form.invoice_payment_term_id = self.payment_term_a
        move = move_form.save()
        self.assertEqual(
            move.alllow_payment_mode_id_filter_domain.ids, self.payment_mode_a.ids
        )

    def test_payment_mode_filter_invoices_term_b(self):
        move_form = Form(
            self.env["account.move"].with_context(
                default_type="out_invoice", company_id=self.company.id
            ),
        )
        move_form.invoice_payment_term_id = self.payment_term_b
        move = move_form.save()
        self.assertEqual(
            move.alllow_payment_mode_id_filter_domain.ids, self.payment_mode_b.ids
        )
