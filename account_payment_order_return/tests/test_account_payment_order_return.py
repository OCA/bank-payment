# Copyright 2017 Tecnativa - Luis M. Ontalba
# Copyright 2021 Tecnativa - João Marques
# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2024 Aurestic - Almudena de La Puente
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0

from datetime import timedelta

from odoo import Command, fields
from odoo.tests import Form
from odoo.tests.common import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class TestAccountPaymentOrderReturn(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.ref("account_payment_order.group_account_payment").write(
            {"users": [(4, cls.env.user.id)]}
        )
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.bank_journal = cls.env["account.journal"].create(
            {"name": "Test Bank Journal", "type": "bank"}
        )
        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "date": "2024-01-01",
                "invoice_date": "2024-01-01",
                "partner_id": cls.partner_a.id,
                "currency_id": cls.currency.id,
                "payment_mode_id": False,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product_a.id,
                            "price_unit": 1000.0,
                            "tax_ids": [],
                        },
                    )
                ],
            }
        )
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
                "partner_ids": [(4, self.partner_a.id)],
                "date_type": "move",
                "filter_date": fields.Date.today() + timedelta(days=1),
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
