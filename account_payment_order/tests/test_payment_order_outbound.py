# © 2017 Camptocamp SA
# © 2017 Creu Blanca
# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime, timedelta

from odoo import Command, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("-at_install", "post_install")
class TestPaymentOrderOutboundBase(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env.user.write(
            {
                "groups_id": [
                    Command.link(
                        cls.env.ref("account_payment_order.group_account_payment").id
                    )
                ]
            }
        )
        cls.company = cls.company_data["company"]
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.payment_method_out = cls.env["account.payment.method"].create(
            {
                "name": "test outbound payment order ok",
                "code": "test_manual",
                "payment_type": "outbound",
                "payment_order_ok": True,
            }
        )
        cls.bank_journal = cls.company_data["default_journal_bank"]
        cls.mode = cls.env["account.payment.method.line"].create(
            {
                "name": "Test Credit Transfer to Suppliers",
                "company_id": cls.company.id,
                "bank_account_link": "variable",
                "journal_id": cls.bank_journal.id,
                "payment_method_id": cls.payment_method_out.id,
            }
        )
        cls.creation_mode = cls.env["account.payment.method.line"].create(
            {
                "name": "Test Direct Debit of suppliers from Société Générale",
                "company_id": cls.company.id,
                "bank_account_link": "variable",
                "journal_id": cls.bank_journal.id,
                "payment_method_id": cls.payment_method_out.id,
            }
        )
        cls.invoice = cls._create_supplier_invoice(cls, "F1242")
        cls.invoice_02 = cls._create_supplier_invoice(cls, "F1243")
        # Make sure no other payment orders are in the DB
        cls.domain = [
            ("state", "=", "draft"),
            ("payment_type", "=", "outbound"),
            ("company_id", "=", cls.company.id),
        ]
        cls.env["account.payment.order"].search(cls.domain).unlink()

    def _create_supplier_invoice(self, ref):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "move_type": "in_invoice",
                "ref": ref,
                "preferred_payment_method_line_id": self.mode.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "name": "product that cost 100",
                            "account_id": self.company_data[
                                "default_account_expense"
                            ].id,
                        },
                    )
                ],
            }
        )

        return invoice

    def _create_supplier_refund(self, move, manual=False):
        if manual:
            # Do the supplier refund manually
            vals = {
                "partner_id": self.partner.id,
                "move_type": "in_refund",
                "ref": move.ref,
                "preferred_payment_method_line_id": self.mode.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1.0,
                            "price_unit": 90.0,
                            "name": "refund of 90.0",
                            "account_id": self.company_data[
                                "default_account_expense"
                            ].id,
                        },
                    )
                ],
            }
            move = self.env["account.move"].create(vals)
            return move
        wizard = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=move.ids)
            .create(
                {
                    "journal_id": move.journal_id.id,
                }
            )
        )
        wizard.refund_moves()
        return wizard.new_move_ids


@tagged("-at_install", "post_install")
class TestPaymentOrderOutbound(TestPaymentOrderOutboundBase):
    def test_creation_due_date(self):
        self.mode.group_lines = False
        self.order_creation("due")

    def test_creation_no_date(self):
        self.mode.group_lines = True
        self.creation_mode.write(
            {
                "group_lines": False,
                "bank_account_link": "fixed",
                "default_date_prefered": "due",
                "journal_id": self.bank_journal.id,
            }
        )
        self.order_creation(False)

    def test_creation_fixed_date(self):
        self.mode.write(
            {
                "bank_account_link": "fixed",
                "default_date_prefered": "fixed",
            }
        )

        self.invoice_02.action_post()
        self.order_creation("fixed")

    def order_creation(self, date_prefered):
        # Open invoice
        self.invoice.action_post()
        order_vals = {
            "payment_type": "outbound",
            "payment_method_line_id": self.creation_mode.id,
        }
        if date_prefered:
            order_vals["date_prefered"] = date_prefered
        order = self.env["account.payment.order"].create(order_vals)
        with self.assertRaises(UserError):
            order.draft2open()

        order.payment_method_line_id = self.mode.id
        self.assertEqual(order.journal_id.id, self.bank_journal.id)

        self.assertEqual(len(order.payment_line_ids), 0)
        if date_prefered:
            self.assertEqual(order.date_prefered, date_prefered)
        with self.assertRaises(UserError):
            order.draft2open()
        line_create = (
            self.env["account.payment.line.create"]
            .with_context(active_model="account.payment.order", active_id=order.id)
            .create(
                {"date_type": "move", "move_date": datetime.now() + timedelta(days=1)}
            )
        )
        line_create.payment_mode = "any"
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
        self.assertGreater(len(order.payment_line_ids), 0)
        order.draft2open()
        order.open2generated()
        order.generated2uploaded()
        self.assertEqual(
            order.payment_line_ids[0].move_line_id.date, order.payment_ids[0].date
        )
        self.assertEqual(order.state, "uploaded")

    def test_account_payment_line_creation_without_payment_mode(self):
        self.invoice.preferred_payment_method_line_id = False
        self.invoice.action_post()
        with self.assertRaises(UserError):
            self.env["account.invoice.payment.line.multi"].with_context(
                active_model="account.move", active_ids=self.invoice.ids
            ).create({}).run()

    def test_cancel_payment_order(self):
        # Open invoice
        self.invoice.action_post()
        # Add to payment order using the wizard
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).run()

        payment_order = self.env["account.payment.order"].search(self.domain)
        self.assertEqual(len(payment_order), 1)

        payment_order.write({"journal_id": self.bank_journal.id})

        self.assertEqual(len(payment_order.payment_line_ids), 1)
        self.assertFalse(payment_order.payment_ids)

        # Open payment order
        payment_order.draft2open()
        self.assertEqual(payment_order.payment_count, 1)
        # Generate and upload
        payment_order.open2generated()
        payment_order.generated2uploaded()

        self.assertEqual(payment_order.state, "uploaded")
        with self.assertRaises(UserError):
            payment_order.unlink()

        payment_order.action_uploaded_cancel()
        self.assertEqual(payment_order.state, "cancel")
        payment_order.cancel2draft()
        payment_order.unlink()
        self.assertEqual(len(self.env["account.payment.order"].search(self.domain)), 0)

    def test_constrains(self):
        outbound_order = self.env["account.payment.order"].create(
            {
                "payment_type": "outbound",
                "payment_method_line_id": self.mode.id,
                "journal_id": self.bank_journal.id,
            }
        )
        with self.assertRaises(ValidationError):
            outbound_order.date_scheduled = date.today() - timedelta(days=2)

    def test_invoice_communication_01(self):
        self.assertEqual(
            "F1242", self.invoice._get_payment_order_communication_direct()
        )
        self.invoice.ref = "F1243"
        self.assertEqual(
            "F1243", self.invoice._get_payment_order_communication_direct()
        )

    def test_invoice_communication_02(self):
        self.invoice.payment_reference = "R1234"
        self.assertEqual(
            "R1234", self.invoice._get_payment_order_communication_direct()
        )

    def test_manual_line_and_manual_date(self):
        # Create payment order
        outbound_order = self.env["account.payment.order"].create(
            {
                "date_prefered": "due",
                "payment_type": "outbound",
                "payment_method_line_id": self.mode.id,
                "journal_id": self.bank_journal.id,
                "description": "order with manual line",
            }
        )
        self.assertEqual(len(outbound_order.payment_line_ids), 0)
        # Create a manual payment order line with custom date
        vals = {
            "order_id": outbound_order.id,
            "partner_id": self.partner.id,
            "communication": "manual line and manual date",
            "currency_id": outbound_order.company_id.currency_id.id,
            "amount_currency": 192.38,
            "date": date.today() + timedelta(days=8),
        }
        self.env["account.payment.line"].create(vals)
        self.assertEqual(len(outbound_order.payment_line_ids), 1)
        self.assertEqual(
            outbound_order.payment_line_ids[0].date, date.today() + timedelta(days=8)
        )
        # Create a manual payment order line with normal date
        vals = {
            "order_id": outbound_order.id,
            "partner_id": self.partner.id,
            "communication": "manual line",
            "currency_id": outbound_order.company_id.currency_id.id,
            "amount_currency": 200.38,
        }
        self.env["account.payment.line"].create(vals)
        self.assertEqual(len(outbound_order.payment_line_ids), 2)
        self.assertEqual(outbound_order.payment_line_ids[1].date, False)
        # Open payment order
        self.assertFalse(outbound_order.payment_ids)
        outbound_order.draft2open()
        self.assertEqual(outbound_order.payment_count, 2)
        self.assertEqual(
            outbound_order.payment_line_ids[0].date,
            outbound_order.payment_line_ids[0].payment_ids.date,
        )
        self.assertEqual(outbound_order.payment_line_ids[1].date, date.today())
        self.assertEqual(
            outbound_order.payment_line_ids[1].date,
            fields.Date.context_today(outbound_order),
        )
        self.assertEqual(
            outbound_order.payment_line_ids[1].payment_ids.date,
            fields.Date.context_today(outbound_order),
        )

    def test_supplier_refund(self):
        """
        Confirm the supplier invoice
        Create a credit note based on that one with an inferior amount
        Confirm the credit note
        Create the payment order
        The communication should be a combination of the invoice reference
        and the credit note one
        """
        self.invoice.action_post()
        self.assertEqual(
            "F1242", self.invoice._get_payment_order_communication_direct()
        )
        self.refund = self._create_supplier_refund(self.invoice)
        self.refund.write({"ref": "R1234"})
        self.refund.invoice_line_ids[0].write({"price_unit": 75.0})

        self.refund.action_post()
        self.assertEqual("R1234", self.refund._get_payment_order_communication_direct())

        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).run()

        payment_order = self.env["account.payment.order"].search(self.domain)
        self.assertEqual(len(payment_order), 1)

        payment_order.write({"journal_id": self.bank_journal.id})

        self.assertEqual(len(payment_order.payment_line_ids), 1)

        self.assertEqual("F1242 R1234", payment_order.payment_line_ids.communication)

    def test_supplier_refund_reference(self):
        """
        Confirm the supplier invoice
        Set a payment referece
        Create a credit note based on that one with an inferior amount
        Confirm the credit note
        Create the payment order
        The communication should be a combination of the invoice payment reference
        and the credit note one
        """
        self.invoice.payment_reference = "F/1234"
        self.invoice.action_post()
        self.assertEqual(
            "F/1234", self.invoice._get_payment_order_communication_direct()
        )
        self.refund = self._create_supplier_refund(self.invoice)
        self.refund.write(
            {
                "ref": "R1234",
                "payment_reference": "FR/1234",
            }
        )
        self.refund.invoice_line_ids[0].write({"price_unit": 75.0})
        self.refund.action_post()
        self.assertEqual(
            "FR/1234", self.refund._get_payment_order_communication_direct()
        )

        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).run()

        payment_order = self.env["account.payment.order"].search(self.domain)
        self.assertEqual(len(payment_order), 1)

        payment_order.write({"journal_id": self.bank_journal.id})

        self.assertEqual(len(payment_order.payment_line_ids), 1)

        self.assertEqual("F/1234 FR/1234", payment_order.payment_line_ids.communication)

    def test_supplier_manual_refund(self):
        """
        Confirm the supplier invoice with reference
        Create a credit note manually
        Confirm the credit note
        Reconcile move lines together
        Create the payment order
        The communication should be a combination of the invoice payment reference
        and the credit note one
        """
        self.invoice.action_post()
        self.assertEqual(
            "F1242", self.invoice._get_payment_order_communication_direct()
        )
        self.refund = self._create_supplier_refund(self.invoice, manual=True)
        self.refund.write({"ref": "R1234"})

        self.refund.action_post()
        self.assertEqual("R1234", self.refund._get_payment_order_communication_direct())

        (self.invoice.line_ids + self.refund.line_ids).filtered(
            lambda line: line.account_type == "liability_payable"
        ).reconcile()

        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).run()

        payment_order = self.env["account.payment.order"].search(self.domain)
        self.assertEqual(len(payment_order), 1)

        payment_order.write({"journal_id": self.bank_journal.id})

        self.assertEqual(len(payment_order.payment_line_ids), 1)

        self.assertEqual("F1242 R1234", payment_order.payment_line_ids.communication)
