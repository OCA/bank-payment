# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Blocking module for Odoo
#    Copyright (C) 2014-2015 ACSONE SA/NV (http://acsone.eu)
#    @author Adrien Peiffer <adrien.peiffer@acsone.eu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp.tests.common as common
from openerp import workflow


def create_simple_invoice(self, cr, uid, payment_term=False, context=None):
    partner_id = self.ref('base.res_partner_2')
    product_id = self.ref('product.product_product_4')
    return self.registry('account.invoice')\
        .create(cr, uid, {'partner_id': partner_id,
                          'account_id':
                          self.ref('account.a_recv'),
                          'payment_term': payment_term,
                          'journal_id':
                          self.ref('account.expenses_journal'),
                          'invoice_line': [(0, 0, {'name': 'test',
                                                   'account_id':
                                                   self.ref('account.a_sale'),
                                                   'price_unit': 2000.00,
                                                   'quantity': 1,
                                                   'product_id': product_id,
                                                   }
                                            )
                                           ],
                          })


class TestAccountBankingPaymentBlocking(common.TransactionCase):

    def setUp(self):
        super(TestAccountBankingPaymentBlocking, self).setUp()
        self.context = self.registry("res.users").context_get(self.cr,
                                                              self.uid)

    def test_invoice(self):
        invoice_obj = self.registry('account.invoice')
        move_line_obj = self.registry('account.move.line')
        invoice_id = create_simple_invoice(self, self.cr, self.uid,
                                           context=self.context)
        invoice_obj.write(self.cr, self.uid, [invoice_id],
                          {'draft_blocked': True})
        workflow.trg_validate(self.uid, 'account.invoice', invoice_id,
                              'invoice_open', self.cr)
        invoice = invoice_obj.browse(self.cr, self.uid, [invoice_id],
                                     context=self.context)[0]
        move_line_ids = move_line_obj\
            .search(self.cr, self.uid, [('account_id.type', 'in',
                                         ['payable', 'receivable']),
                                        ('invoice.id', '=', invoice.id)])
        move_line = move_line_obj.browse(self.cr, self.uid, move_line_ids)[0]
        self.assertTrue(move_line.blocked)
        self.assertEqual(invoice.blocked, move_line.blocked,
                         'Blocked values are not equals')
        move_line_obj.write(self.cr, self.uid, move_line_ids,
                            {'blocked': False})
        invoice = invoice_obj.browse(self.cr, self.uid, [invoice_id],
                                     context=self.context)[0]
        move_line = move_line_obj.browse(self.cr, self.uid, move_line_ids)[0]
        self.assertEqual(invoice.blocked, move_line.blocked,
                         'Blocked values are not equals')

    def test_invoice_payment_term(self):
        invoice_obj = self.registry('account.invoice')
        move_line_obj = self.registry('account.move.line')
        payment_term_advance = self.ref('account.account_payment_term_advance')
        invoice_id = create_simple_invoice(self, self.cr, self.uid,
                                           payment_term=payment_term_advance,
                                           context=self.context)
        invoice_obj.write(self.cr, self.uid, [invoice_id],
                          {'draft_blocked': True})
        workflow.trg_validate(self.uid, 'account.invoice', invoice_id,
                              'invoice_open', self.cr)
        invoice = invoice_obj.browse(self.cr, self.uid, [invoice_id],
                                     context=self.context)[0]
        move_line_ids = move_line_obj\
            .search(self.cr, self.uid, [('account_id.type', 'in',
                                         ['payable', 'receivable']),
                                        ('invoice.id', '=', invoice.id)])
        move_lines = move_line_obj.browse(self.cr, self.uid, move_line_ids)
        self.assertTrue(
            move_lines and all(line.blocked for line in move_lines) or False)
        move_line_obj.write(self.cr, self.uid, move_line_ids,
                            {'blocked': False})
        invoice = invoice_obj.browse(self.cr, self.uid, [invoice_id],
                                     context=self.context)[0]
        self.assertEqual(invoice.blocked, False,
                         'Blocked values are not equals')
