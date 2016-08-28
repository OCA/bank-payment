# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common


class TestAccountPaymentTransferReconcileBatch(common.TransactionCase):
    def setUp(self):
        super(TestAccountPaymentTransferReconcileBatch, self).setUp()
        self.journal = self.env['account.journal'].create({
            'name': 'Test journal',
            'type': 'general',
            'code': 'TEST',
        })
        self.bank_account = self.env['res.partner.bank'].create({
            'state': 'bank',
            'acc_number': 'TEST',
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner',
            'supplier': True,
        })
        self.mode = self.env['payment.mode'].create({
            'name': 'Test payment mode',
            'journal': self.journal.id,
            'bank_id': self.bank_account.id,
            'transfer_journal_id': self.journal.id,
            'transfer_account_id': self.partner.property_account_payable.id,
            'type': self.env.ref(
                'account_banking_payment_export.manual_bank_tranfer').id,
        })
        self.product = self.env['product.product'].create({
            'name': 'Test product',
        })
        self.invoice = self.env['account.invoice'].create({
            'type': 'in_invoice',
            'partner_id': self.partner.id,
            'account_id': self.partner.property_account_payable.id,
            'invoice_line': [
                (0, 0, {
                    'product_id': self.product.id,
                    'name': self.product.name,
                    'price_unit': 20,
                }),
            ]
        })
        self.invoice.signal_workflow('invoice_open')
        self.payment_order = self.env['payment.order'].create({
            'mode': self.mode.id,
        })
        line = self.invoice.move_id.line_id.filtered(
            lambda x: x.account_id == self.invoice.account_id)
        wizard = self.env['payment.order.create'].with_context(
            active_model='payment.order', active_id=self.payment_order.id
        ).create({})
        line_vals = wizard._prepare_payment_line(self.payment_order, line)
        self.payment_line = self.env['payment.line'].create(line_vals)

    def test_enqueue(self):
        self.payment_order.signal_workflow('open')
        self.payment_order.action_open()
        self.payment_order.with_context(test_connector=True).action_sent()
        func = "openerp.addons.account_payment_transfer_reconcile_batch." \
               "models.payment_order.reconcile_one_move('bank.payment.line', "
        job = self.env['queue.job'].sudo().search(
            [('func_string', 'like', "%s%%" % func)])
        self.assertTrue(job)
