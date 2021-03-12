# Copyright 2017 Tecnativa - Luis M. Ontalba
# Copyright 2021 Tecnativa - João Marques
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0

from odoo import fields
from odoo.tests import common
from odoo.tests.common import Form


class TestAccountPaymentOrderReturn(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountPaymentOrderReturn, cls).setUpClass()
        cls.account_type = cls.env["account.account.type"].create(
            {
                "name": "Test Account Type",
                "type": "receivable",
                "internal_group": "income",
            }
        )
        cls.a_receivable = cls.env["account.account"].create(
            {
                "code": "TAA",
                "name": "Test Receivable Account",
                "reconcile": True,
                "internal_type": "receivable",
                "user_type_id": cls.account_type.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner 2"})
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test Journal", "type": "bank", "code": "Test"}
        )
        move_form = Form(
            cls.env["account.move"].with_context(default_type="out_invoice")
        )
        move_form.partner_id = cls.partner
        with move_form.invoice_line_ids.new() as line_form:
            line_form.name = "Test line"
            line_form.account_id = cls.a_receivable
            line_form.quantity = 1.0
            line_form.price_unit = 100.00
        cls.invoice = move_form.save()
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test payment mode",
                "fixed_journal_id": cls.invoice.journal_id.id,
                "bank_account_link": "variable",
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
        wizard = wizard_o.with_context(context).create(
            {
                "order_id": self.payment_order.id,
                "journal_ids": [(4, self.journal.id), (4, self.invoice.journal_id.id)],
                "allow_blocked": True,
                "date_type": "move",
                "move_date": fields.Date.today(),
                "payment_mode": "any",
                "invoice": True,
                "include_returned": True,
            }
        )
        wizard.populate()
        self.assertTrue(len(wizard.move_line_ids), 1)
        self.receivable_line = self.invoice.line_ids.filtered(
            lambda x: x.account_id.internal_type == "receivable"
        )
        # Invert the move to simulate the payment
        self.payment_move = self.env["account.move"].create(
            self.invoice._reverse_move_vals(default_values={})
        )
        self.payment_move.action_post()
        self.payment_line = self.payment_move.line_ids.filtered(
            lambda x: x.account_id.internal_type == "receivable"
        )
        # Reconcile both
        (self.receivable_line | self.payment_line).reconcile()
        # prev_move_lines
        wizard.include_returned = False
        wizard.populate()
        prev_move_lines = wizard.move_line_ids
        # Create payment return
        self.payment_return = self.env["payment.return"].create(
            {
                "journal_id": self.journal.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.partner.id,
                            "move_line_ids": [(6, 0, self.payment_line.ids)],
                            "amount": self.payment_line.credit,
                        },
                    )
                ],
            }
        )
        self.payment_return.action_confirm()
        wizard.include_returned = False
        wizard.populate()
        self.assertTrue((wizard.move_line_ids - prev_move_lines), 1)
