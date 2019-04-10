# -*- coding: utf-8 -*-
# Copyright 2014-2015 ACSONE SA/NV (http://acsone.eu)
# Author: Adrien Peiffer <adrien.peiffer@acsone.eu>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestAccountBankingPaymentBlocking(TransactionCase):

    def create_simple_invoice(self, payment_term=False):
        partner = self.env.ref('base.res_partner_2')
        product = self.env.ref('product.product_product_4')
        return self.env['account.invoice'].create({
            'partner_id': partner.id,
            'account_id': self.env.ref('account.a_recv').id,
            'payment_term': payment_term,
            'journal_id': self.env.ref('account.expenses_journal').id,
            'invoice_line': [(0, 0, {
                'name': 'test',
                'account_id': self.env.ref('account.a_sale').id,
                'price_unit': 2000.00,
                'quantity': 1,
                'product_id': product.id,
            })],
        })

    def test_invoice(self):
        move_line_obj = self.env['account.move.line']
        invoice = self.create_simple_invoice()

        # Block invoice
        invoice.write({'draft_blocked': True})
        invoice.signal_workflow('invoice_open')
        move_lines = move_line_obj.search([
            ('account_id.type', 'in', ['payable', 'receivable']),
            ('invoice.id', '=', invoice.id)
        ])
        move_line = move_lines[:1]
        self.assertTrue(move_line.blocked)
        self.assertEqual(invoice.blocked, move_line.blocked)
        self.assertIn(invoice, invoice.search([('blocked', '=', True)]))
        self.assertNotIn(invoice, invoice.search([('blocked', '=', False)]))

        # Unblock invoice
        move_lines.write({'blocked': False})
        invoice.env.invalidate_all()
        self.assertEqual(invoice.blocked, move_line.blocked)
        self.assertIn(invoice, invoice.search([('blocked', '=', False)]))
        self.assertNotIn(invoice, invoice.search([('blocked', '=', True)]))

    def test_invoice_payment_term(self):
        move_line_obj = self.env['account.move.line']
        term_advance = self.env.ref('account.account_payment_term_advance')
        invoice = self.create_simple_invoice(payment_term=term_advance.id)

        # Block invoice
        invoice.write({'draft_blocked': True})
        invoice.signal_workflow('invoice_open')
        move_lines = move_line_obj.search([
            ('account_id.type', 'in', ['payable', 'receivable']),
            ('invoice.id', '=', invoice.id)
        ])
        self.assertTrue(
            move_lines and all(line.blocked for line in move_lines) or False)

        # Unblock invoice
        move_lines.write({'blocked': False})
        invoice.env.invalidate_all()
        self.assertEqual(invoice.blocked, False)
