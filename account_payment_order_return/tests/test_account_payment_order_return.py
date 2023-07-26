# Copyright 2017 Tecnativa - Luis M. Ontalba
# Copyright 2021 Tecnativa - João Marques
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0

from datetime import timedelta

from odoo import fields
from odoo.tests import common
from odoo.tests.common import Form


class TestAccountPaymentOrderReturn(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner 2"})
        cls.sale_journal = cls.env["account.journal"].create(
            {"name": "Test Sale Journal", "type": "sale", "code": "Test"}
        )
        cls.bank_journal = cls.env["account.journal"].create(
            {"name": "Test Bank Journal", "type": "bank"}
        )
        move_form = Form(
            cls.env["account.move"].with_context(
                default_move_type="out_invoice", default_journal_id=cls.sale_journal.id
            )
        )
        move_form.partner_id = cls.partner
        uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product_order = cls.env["product.product"].create(
            {
                "name": "Zed+ Antivirus",
                "standard_price": 235.0,
                "list_price": 280.0,
                "type": "consu",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "default_code": "PROD_ORDER",
                "taxes_id": False,
            }
        )
        with move_form.invoice_line_ids.new() as line_form:
            line_form.name = "Test line"
            line_form.product_id = cls.product_order
            line_form.quantity = 1.0
            line_form.price_unit = 100.00
        cls.invoice = move_form.save()
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test payment mode",
                "fixed_journal_id": cls.bank_journal.id,
                "bank_account_link": "fixed",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )
        cls.payment_order = cls.env["account.payment.order"].create(
            {
                "payment_mode_id": cls.payment_mode.id,
                "date_prefered": "due",
                "payment_type": "inbound",
            }
        )

    def test_global(self):
        self.invoice.action_post()
        wizard_o = self.env["account.payment.line.create"]
        context = wizard_o._context.copy()
        context.update(
            {
                "active_model": "account.payment.order",
                "active_id": self.payment_order.id,
            }
        )
        wizard = wizard_o.with_context(**context).create(
            {
                "order_id": self.payment_order.id,
                "journal_ids": [
                    (4, self.bank_journal.id),
                    (4, self.invoice.journal_id.id),
                ],
                "partner_ids": [(4, self.partner.id)],
                "allow_blocked": True,
                "date_type": "move",
                "move_date": fields.Date.today() + timedelta(days=1),
                "payment_mode": "any",
                "invoice": True,
                "include_returned": True,
            }
        )
        wizard.populate()
        self.assertEqual(len(wizard.move_line_ids), 1)
        payment_register = Form(
            self.env["account.payment.register"].with_context(
                active_model="account.move", active_ids=self.invoice.ids
            )
        )
        self.payment = payment_register.save()._create_payments()
        if self.payment.state != "posted":
            self.payment.action_post()
        wizard.populate()
        # Create payment return
        payment_return_form = Form(self.env["payment.return"])
        payment_return_form.journal_id = self.bank_journal
        with payment_return_form.line_ids.new() as line_form:
            line_form.move_line_ids.add(
                self.payment.move_id.line_ids.filtered(
                    lambda x: x.account_id.account_type == "asset_receivable"
                )
            )
        self.payment_return = payment_return_form.save()
        self.payment_return.action_confirm()
        wizard.include_returned = False
        wizard.populate()
        self.assertEqual(len(wizard.move_line_ids), 0)
