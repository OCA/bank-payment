# © 2017 Camptocamp SA
# © 2017 Creu Blanca
# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime, timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("-at_install", "post_install")
class TestPaymentOrderOutboundBase(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.company = cls.company_data["company"]
        cls.env.user.company_id = cls.company.id
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "bank_ids": [
                    (
                        0,
                        0,
                        {
                            "acc_number": "TEST-NUMBER",
                        },
                    )
                ],
            }
        )
        cls.invoice_line_account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST1",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
            }
        )
        cls.mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test Credit Transfer to Suppliers",
                "company_id": cls.company.id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
            }
        )
        cls.creation_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test Direct Debit of suppliers from Société Générale",
                "company_id": cls.company.id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
            }
        )
        cls.invoice = cls._create_supplier_invoice(cls, "F1242")
        cls.invoice_02 = cls._create_supplier_invoice(cls, "F1243")
        cls.bank_journal = cls.company_data["default_journal_bank"]
        # Make sure no other payment orders are in the DB
        cls.domain = [
            ("state", "=", "draft"),
            ("payment_type", "=", "outbound"),
            ("company_id", "=", cls.env.user.company_id.id),
        ]
        cls.env["account.payment.order"].search(cls.domain).unlink()

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
                            "product_id": self.env.ref("product.product_product_4").id,
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

    def _create_supplier_refund(self, move, manual=False):
        if manual:
            # Do the supplier refund manually
            vals = {
                "partner_id": self.partner.id,
                "move_type": "in_refund",
                "ref": move.ref,
                "payment_mode_id": self.mode.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        None,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1.0,
                            "price_unit": 90.0,
                            "name": "refund of 90.0",
                            "account_id": self.invoice_line_account.id,
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
                    "date_mode": "entry",
                    "refund_method": "refund",
                    "journal_id": move.journal_id.id,
                }
            )
        )
        wizard.reverse_moves()
        return wizard.new_move_ids


@tagged("-at_install", "post_install")
class TestPaymentOrderOutbound(TestPaymentOrderOutboundBase):
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
        self.assertGreater(len(order.payment_line_ids), 0)
        self.assertFalse(order.partner_banks_archive_msg)
        order.payment_line_ids.partner_bank_id.action_archive()
        self.assertTrue(order.partner_banks_archive_msg)
        order.payment_line_ids.partner_bank_id.action_unarchive()
        self.assertFalse(order.partner_banks_archive_msg)
        order.draft2open()
        order.open2generated()
        order.generated2uploaded()
        self.assertEqual(order.move_ids[0].date, order.payment_ids[0].date)
        self.assertEqual(order.state, "uploaded")

    def test_account_payment_line_creation_without_payment_mode(self):
        self.invoice.payment_mode_id = False
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
                "payment_mode_id": self.mode.id,
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
            "F1242", self.invoice._get_payment_order_communication_direct()
        )

    def test_manual_line_and_manual_date(self):
        # Create payment order
        outbound_order = self.env["account.payment.order"].create(
            {
                "date_prefered": "due",
                "payment_type": "outbound",
                "payment_mode_id": self.mode.id,
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
            "currency_id": outbound_order.payment_mode_id.company_id.currency_id.id,
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
            "currency_id": outbound_order.payment_mode_id.company_id.currency_id.id,
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
            outbound_order.payment_line_ids[0].payment_ids.date, fields.Date.today()
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

    def test_partial_reconciliation(self):
        """
        Confirm both supplier invoices
        Add invoices to payment order
        Reduce payment amount of first invoice from 100 to 80
        Take payment order all the way to uploaded
        Confirm 80 reconciled with first, not second invoice

        generated2uploaded() does partial reconciliation of non-matching
        line amounts before running .reconcile() against the remaining
        matching line amounts.
        """
        # Open both invoices
        self.invoice.action_post()
        self.assertEqual(
            "F1242", self.invoice._get_payment_order_communication_direct()
        )
        self.invoice_02.action_post()
        self.assertEqual(
            "F1243", self.invoice_02._get_payment_order_communication_direct()
        )

        # Add to payment order using the wizard
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move",
            active_ids=self.invoice.ids + self.invoice_02.ids,
        ).create({}).run()

        payment_order = self.env["account.payment.order"].search(self.domain)
        self.assertEqual(len(payment_order), 1)

        payment_order.write({"journal_id": self.bank_journal.id})

        self.assertEqual(len(payment_order.payment_line_ids), 2)
        self.assertFalse(payment_order.payment_ids)

        # Reduce payment of first invoice from 100 to 80
        first_payment_line, second_payment_line = payment_order.payment_line_ids
        first_payment_line.write({"amount_currency": 80.0})

        # Open payment order
        payment_order.draft2open()

        # Confirm single payment (grouped - two invoices one partner)
        self.assertEqual(payment_order.payment_count, 1)

        # Generate and upload
        payment_order.open2generated()
        payment_order.generated2uploaded()

        self.assertEqual(payment_order.state, "uploaded")
        with self.assertRaises(UserError):
            payment_order.unlink()

        # Confirm payments were reconciled against correct invoices
        self.assertEqual(first_payment_line.amount_currency, 80.0)
        self.assertEqual(
            first_payment_line.move_line_id.amount_residual_currency, -20.0
        )
        self.assertEqual(second_payment_line.amount_currency, 100.0)
        self.assertEqual(second_payment_line.move_line_id.amount_residual_currency, 0.0)

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
        with Form(self.refund) as refund_form:
            refund_form.ref = "R1234"
            with refund_form.invoice_line_ids.edit(0) as line_form:
                line_form.price_unit = 75.0

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
            "F1242", self.invoice._get_payment_order_communication_direct()
        )
        self.refund = self._create_supplier_refund(self.invoice)
        with Form(self.refund) as refund_form:
            refund_form.ref = "R1234"
            refund_form.payment_reference = "FR/1234"
            with refund_form.invoice_line_ids.edit(0) as line_form:
                line_form.price_unit = 75.0

        self.refund.action_post()
        self.assertEqual("R1234", self.refund._get_payment_order_communication_direct())

        # The user add the outstanding payment to the invoice
        invoice_line = self.invoice.line_ids.filtered(
            lambda line: line.account_internal_type == "payable"
        )
        refund_line = self.refund.line_ids.filtered(
            lambda line: line.account_internal_type == "payable"
        )
        (invoice_line | refund_line).reconcile()

        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).run()

        payment_order = self.env["account.payment.order"].search(self.domain)
        self.assertEqual(len(payment_order), 1)

        payment_order.write({"journal_id": self.bank_journal.id})

        self.assertEqual(len(payment_order.payment_line_ids), 1)

        self.assertEqual("F1242 R1234", payment_order.payment_line_ids.communication)
        self.assertNotIn("FR/1234", payment_order.payment_line_ids.communication)

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
        with Form(self.refund) as refund_form:
            refund_form.ref = "R1234"

        self.refund.action_post()
        self.assertEqual("R1234", self.refund._get_payment_order_communication_direct())

        (self.invoice.line_ids + self.refund.line_ids).filtered(
            lambda line: line.account_internal_type == "payable"
        ).reconcile()

        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=self.invoice.ids
        ).create({}).run()

        payment_order = self.env["account.payment.order"].search(self.domain)
        self.assertEqual(len(payment_order), 1)

        payment_order.write({"journal_id": self.bank_journal.id})

        self.assertEqual(len(payment_order.payment_line_ids), 1)

        self.assertEqual("F1242 R1234", payment_order.payment_line_ids.communication)
