# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0

from odoo.tests import common
from odoo import fields


class TestAccountPaymentOrderReturn(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountPaymentOrderReturn, cls).setUpClass()
        cls.account_type = cls.env['account.account.type'].create({
            'name': 'Test Account Type'})
        cls.a_receivable = cls.env['account.account'].create({
            'code': 'TAA',
            'name': 'Test Receivable Account',
            'internal_type': 'receivable',
            'user_type_id': cls.account_type.id,
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner 2',
            'parent_id': False,
        })
        cls.journal = cls.env['account.journal'].create({
            'name': 'Test Journal',
            'type': 'bank',
        })
        cls.invoice = cls.env['account.invoice'].create({
            'name': 'Test Invoice 3',
            'partner_id': cls.partner.id,
            'type': 'out_invoice',
            'journal_id': cls.journal.id,
            'invoice_line_ids': [(0, 0, {
                'account_id': cls.a_receivable.id,
                'name': 'Test line',
                'quantity': 1.0,
                'price_unit': 100.00,
            })],
        })
        cls.payment_mode = cls.env['account.payment.mode'].create({
            'name': 'Test payment mode',
            'fixed_journal_id': cls.journal.id,
            'bank_account_link': 'variable',
            'payment_method_id': cls.env.ref(
                'account.account_payment_method_manual_in').id})
        cls.payment_order = cls.env['account.payment.order'].create({
            'payment_mode_id': cls.payment_mode.id,
            'date_prefered': 'due',
            'payment_type': 'inbound',
        })

    def test_global(self):
        self.invoice.action_invoice_open()
        wizard_o = self.env['account.payment.line.create']
        context = wizard_o._context.copy()
        context.update({
            'active_model': 'account.payment.order',
            'active_id': self.payment_order.id,
        })
        wizard = wizard_o.with_context(context).create({
            'order_id': self.payment_order.id,
            'journal_ids': [(4, self.journal.id)],
            'allow_blocked': True,
            'date_type': 'move',
            'move_date': fields.Date.today(),
            'payment_mode': 'any',
            'invoice': True,
            'include_returned': True,

        })
        wizard.populate()
        self.assertTrue(len(wizard.move_line_ids), 1)
        self.receivable_line = self.invoice.move_id.line_ids.filtered(
            lambda x: x.account_id.internal_type == 'receivable')
        # Invert the move to simulate the payment
        self.payment_move = self.invoice.move_id.copy({
            'journal_id': self.journal.id
        })
        for move_line in self.payment_move.line_ids:
            move_line.with_context(check_move_validity=False).write({
                'debit': move_line.credit, 'credit': move_line.debit})
        self.payment_line = self.payment_move.line_ids.filtered(
            lambda x: x.account_id.internal_type == 'receivable')
        # Reconcile both
        (self.receivable_line | self.payment_line).reconcile()
        # Create payment return
        self.payment_return = self.env['payment.return'].create(
            {'journal_id': self.journal.id,
             'line_ids': [
                 (0, 0, {'partner_id': self.partner.id,
                         'move_line_ids': [(6, 0, self.payment_line.ids)],
                         'amount': self.payment_line.credit})]})
        self.payment_return.action_confirm()
        wizard.include_returned = False
        wizard.populate()
        self.assertFalse(wizard.move_line_ids)
