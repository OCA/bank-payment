# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestPaymentOrder(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.ref("base.main_company")
        self.env.user.company_id = self.company.id
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        self.product = self.env["product.product"].create({"name": "Test"})
        self.invoice_line_account = self.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST1",
                "user_type_id": self.env.ref("account.data_account_type_expenses").id,
            }
        )
        self.bank_journal = self.env["account.journal"].search(
            [("company_id", "=", self.company.id), ("type", "=", "bank")], limit=1
        )
        self.transfer_journal = self.env["account.journal"].search(
            [("company_id", "=", self.company.id), ("type", "=", "general")],
            limit=1,
        )

        self.mode = self.env["account.payment.mode"].create(
            {
                "name": "Test Credit Transfer to Suppliers",
                "company_id": self.company.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "fixed_journal_id": self.bank_journal.id,
                "bank_account_link": "fixed",
            }
        )
        self.invoice = self._create_supplier_invoice("F1242")
        # Make sure no other payment orders are in the DB
        self.domain = [
            ("state", "=", "draft"),
            ("payment_type", "=", "outbound"),
            ("company_id", "=", self.env.user.company_id.id),
        ]
        self.env["account.payment.order"].search(self.domain).unlink()

    def _create_supplier_invoice(self, ref):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "move_type": "in_invoice",
                "ref": ref,
                "payment_mode_id": self.mode.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        None,
                        {
                            "product_id": self.product.id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "name": "product that cost 100",
                            "account_id": self.invoice_line_account.id,
                        },
                    )
                ],
            }
        )

        return invoice

    def test_payment_order_transfer_jounral(self):
        self.invoice.action_post()
        self.bank_journal.transfer_journal_id = self.transfer_journal
        order_vals = {
            "payment_type": "outbound",
            "payment_mode_id": self.mode.id,
        }
        order = self.env["account.payment.order"].create(order_vals)
        order.payment_mode_id = self.mode.id
        order.payment_mode_id_change()
        self.assertEqual(order.journal_id.id, self.bank_journal.id)

        self.assertEqual(len(order.payment_line_ids), 0)
        line_create = (
            self.env["account.payment.line.create"]
            .with_context(active_model="account.payment.order", active_id=order.id)
            .create(
                {"date_type": "move", "move_date": datetime.now() + timedelta(days=1)}
            )
        )
        line_create.payment_mode = "any"
        line_create.move_line_filters_change()
        line_create.populate()
        line_create.create_payment_lines()
        line_created_due = (
            self.env["account.payment.line.create"]
            .with_context(active_model="account.payment.order", active_id=order.id)
            .create(
                {"date_type": "due", "due_date": datetime.now() + timedelta(days=1)}
            )
        )
        line_created_due.populate()
        line_created_due.create_payment_lines()
        order.draft2open()
        order.open2generated()
        order.generated2uploaded()
        self.assertEqual(order.move_ids[0].journal_id, self.transfer_journal)
