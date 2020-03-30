# © 2017 Camptocamp SA
# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestPaymentOrderOutbound(TransactionCase):
    def setUp(self):
        super(TestPaymentOrderOutbound, self).setUp()
        self.journal = self.env["account.journal"].search(
            [("type", "=", "bank")], limit=1
        )
        self.invoice_line_account = (
            self.env["account.account"]
            .search(
                [
                    (
                        "user_type_id",
                        "=",
                        self.env.ref("account.data_account_type_expenses").id,
                    )
                ],
                limit=1,
            )
            .id
        )
        self.invoice = self._create_supplier_invoice()
        self.invoice_02 = self._create_supplier_invoice()
        self.mode = self.env.ref("account_payment_mode.payment_mode_outbound_ct1")
        self.creation_mode = self.env.ref(
            "account_payment_mode.payment_mode_outbound_dd1"
        )
        self.bank_journal = self.env["account.journal"].search(
            [("type", "=", "bank")], limit=1
        )
        # Make sure no other payment orders are in the DB
        self.domain = [("state", "=", "draft"), ("payment_type", "=", "outbound")]
        self.env["account.payment.order"].search(self.domain).unlink()

    def _create_supplier_invoice(self):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.env.ref("base.res_partner_4").id,
                "type": "in_invoice",
                "payment_mode_id": self.env.ref(
                    "account_payment_mode.payment_mode_outbound_ct1"
                ).id,
                "invoice_line_ids": [
                    (
                        0,
                        None,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "name": "product that cost 100",
                            "account_id": self.invoice_line_account,
                        },
                    )
                ],
            }
        )

        return invoice

    def test_creation_due_date(self):
        self.mode.variable_journal_ids = self.bank_journal
        self.mode.group_lines = False
        self.order_creation("due")

    def test_creation_no_date(self):
        self.mode.group_lines = True
        self.creation_mode.write(
            {
                "group_lines": False,
                "bank_account_link": "fixed",
                "default_date_prefered": "due",
                "fixed_journal_id": self.bank_journal.id,
            }
        )
        self.mode.variable_journal_ids = self.bank_journal
        self.order_creation(False)

    def test_creation_fixed_date(self):
        self.mode.write(
            {
                "bank_account_link": "fixed",
                "default_date_prefered": "fixed",
                "fixed_journal_id": self.bank_journal.id,
            }
        )

        self.invoice_02.action_post()
        self.order_creation("fixed")

    def order_creation(self, date_prefered):
        # Open invoice
        self.invoice.action_post()
        order_vals = {
            "payment_type": "outbound",
            "payment_mode_id": self.creation_mode.id,
        }
        if date_prefered:
            order_vals["date_prefered"] = date_prefered
        order = self.env["account.payment.order"].create(order_vals)
        with self.assertRaises(UserError):
            order.draft2open()

        order.payment_mode_id = self.mode.id
        order.payment_mode_id_change()
        self.assertEqual(order.journal_id.id, self.bank_journal.id)

        self.assertEqual(len(order.payment_line_ids), 0)
        if date_prefered:
            self.assertEqual(order.date_prefered, date_prefered)
        with self.assertRaises(UserError):
            order.draft2open()
        line_create = (
            self.env["account.payment.line.create"]
            .with_context(active_model="account.payment.order", active_id=order.id)
            .create({"date_type": "move", "move_date": datetime.now()})
        )
        line_create.payment_mode = "any"
        line_create.move_line_filters_change()
        line_create.populate()
        line_create.create_payment_lines()
        line_created_due = (
            self.env["account.payment.line.create"]
            .with_context(active_model="account.payment.order", active_id=order.id)
            .create({"date_type": "due", "due_date": datetime.now()})
        )
        line_created_due.populate()
        line_created_due.create_payment_lines()
        self.assertGreater(len(order.payment_line_ids), 0)
        order.draft2open()
        order.open2generated()
        order.generated2uploaded()
        order.action_done()
        self.assertEqual(order.state, "done")

    def test_cancel_payment_order(self):
        # Open invoice
        self.invoice.action_post()
        # Add to payment order using the wizard
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).run()

        payment_order = self.env["account.payment.order"].search(self.domain)
        self.assertEqual(len(payment_order), 1)
        bank_journal = self.env["account.journal"].search(
            [("type", "=", "bank")], limit=1
        )
        # Set journal to allow cancelling entries
        bank_journal.update_posted = True

        payment_order.write({"journal_id": bank_journal.id})

        self.assertEqual(len(payment_order.payment_line_ids), 1)
        self.assertEqual(len(payment_order.bank_line_ids), 0)

        # Open payment order
        payment_order.draft2open()

        self.assertEqual(payment_order.bank_line_count, 1)

        # Generate and upload
        payment_order.open2generated()
        payment_order.generated2uploaded()

        self.assertEqual(payment_order.state, "uploaded")
        with self.assertRaises(UserError):
            payment_order.unlink()

        bank_line = payment_order.bank_line_ids

        with self.assertRaises(UserError):
            bank_line.unlink()
        payment_order.action_done_cancel()
        self.assertEqual(payment_order.state, "cancel")
        payment_order.cancel2draft()
        payment_order.unlink()
        self.assertEqual(len(self.env["account.payment.order"].search(self.domain)), 0)

    def test_constrains(self):
        outbound_order = self.env["account.payment.order"].create(
            {
                "payment_type": "outbound",
                "payment_mode_id": self.mode.id,
                "journal_id": self.journal.id,
            }
        )
        with self.assertRaises(ValidationError):
            outbound_order.date_scheduled = date.today() - timedelta(days=1)
