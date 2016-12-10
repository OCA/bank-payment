# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common


class TestAccountPaymentTransferReconcileBatch(common.TransactionCase):
    def setUp(self):
        super(TestAccountPaymentTransferReconcileBatch, self).setUp()
        self.method = self.env['account.payment.method'].create({
            'name': 'Test Transfer',
            'code': 'test_code_transfer',
            'payment_type': 'outbound',
        })
        self.journal = self.env['account.journal'].create({
            'name': 'Test journal',
            'type': 'general',
            'code': 'TEST',
            'outbound_payment_method_ids': [(6, 0, self.method.ids)]
        })
        self.account_type = self.env['account.account.type'].create({
            'name': 'Test account type',
            'type': 'other',
        })
        self.account_expenses = self.env['account.account'].create({
            'name': 'Test expenses account',
            'code': 'test_account',
            'user_type_id': self.account_type.id,
        })
        self.bank_account = self.env['res.partner.bank'].create({
            'acc_number': 'TEST',
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner',
            'supplier': True,
        })
        self.mode = self.env['account.payment.mode'].create({
            'name': 'Test payment mode',
            'bank_account_link': 'fixed',
            'offsetting_account': 'transfer_account',
            'payment_method_id': self.method.id,
            'fixed_journal_id': self.journal.id,
            'transfer_journal_id': self.journal.id,
            'transfer_account_id': self.partner.property_account_payable_id.id,
        })
        self.product = self.env['product.product'].create({
            'name': 'Test product',
            'property_account_expense_id': 1,
        })
        self.invoice = self.env['account.invoice'].create({
            'type': 'in_invoice',
            'partner_id': self.partner.id,
            'account_id': self.partner.property_account_payable_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product.id,
                    'name': self.product.name,
                    'price_unit': 20,
                    'account_id': self.account_expenses.id,
                }),
            ]
        })
        self.invoice.signal_workflow('invoice_open')
        self.payment_order = self.env['account.payment.order'].create({
            'payment_type': 'outbound',
            'payment_mode_id': self.mode.id,
        })

        line = self.invoice.move_id.line_ids.filtered(
            lambda x: x.account_id == self.invoice.account_id)

        wizard = self.env['account.payment.line.create'].with_context(
            active_model='account.payment.order',
            active_id=self.payment_order.id
        ).create({})
        wizard.move_line_ids = line
        wizard.move_line_ids = line
        wizard.create_payment_lines()

    def test_enqueue(self):
        self.payment_order.draft2open()
        self.payment_order.with_context(test_connector=True).generate_move()
        func = "openerp.addons.account_payment_transfer_reconcile_batch." \
               "models.bank_payment_line.reconcile_one_move(" \
               "'bank.payment.line'"
        job = self.env['queue.job'].sudo().search(
            [('func_string', 'like', "%s%%" % func)])
        self.assertTrue(job)
        # Check domain queued moves
        other_payment_order = self.env['account.payment.order'].create({
            'payment_type': 'outbound',
            'payment_mode_id': self.mode.id,
        })
        wizard = self.env['account.payment.line.create'].with_context(
            active_model='account.payment.order',
            active_id=other_payment_order.id
        ).create({})
        domain = wizard._prepare_move_line_domain()
        lines = self.env['account.move.line'].search(domain)
        self.assertFalse(lines)
