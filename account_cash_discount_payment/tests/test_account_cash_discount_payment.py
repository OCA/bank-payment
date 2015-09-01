# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
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
from openerp import workflow, fields


def create_simple_invoice(self, date):
    journal_id = self.ref('account.sales_journal')
    partner_id = self.ref('base.res_partner_4')
    product_id = self.ref('product.product_product_4')
    return self.env['account.invoice']\
        .create({'partner_id': partner_id,
                 'account_id':
                 self.ref('account.a_pay'),
                 'journal_id':
                 journal_id,
                 'date_invoice': date,
                 'discount_due_date': date,
                 'discount_amount': 1500,
                 'type': 'in_invoice',
                 'invoice_line': [(0, 0, {'name': 'test',
                                          'account_id':
                                          self.ref('account.a_expense'),
                                          'price_unit': 2000.00,
                                          'quantity': 1,
                                          'product_id': product_id,
                                          }
                                   )
                                  ],
                 })


class TestAccountCashDiscountBase(common.TransactionCase):

    def setUp(self):
        super(TestAccountCashDiscountBase, self).setUp()
        self.context = self.registry("res.users").context_get(self.cr,
                                                              self.uid)

    def test_invoice_payment_discount(self):
        date = fields.Date.today()
        invoice = create_simple_invoice(self, date)
        workflow.trg_validate(self.uid, 'account.invoice', invoice.id,
                              'invoice_open', self.cr)
        # Ensure linked move is posted
        move = invoice.move_id
        move.button_validate()
        self.assertEqual(move.state, 'posted',
                         'Journal Entries are not in posted state')
        payment_order_create_obj = self.env['payment.order.create']
        account_payment_id = self.ref('account_payment.payment_order_1')
        payment_order_create = payment_order_create_obj.create(
            {'cash_discount_date_start': date,
             'cash_discount_date_end': date,
             'cash_discount_date': True,
             'populate_results': True})
        ctx = self.context.copy()
        ctx.update({'active_id': account_payment_id})
        res = payment_order_create.with_context(ctx).search_entries()
        payment_order_create.entries = res['context']['line_ids']
        payment_order_create.with_context(ctx).create_payment()
        account_payment = self.env['payment.order']\
            .browse([account_payment_id])
        self.assertEqual(len(account_payment.line_ids.ids), 1,
                         "Number of line isn't correct")
        line = account_payment.line_ids[0]
        self.assertAlmostEqual(line.discount_amount, 500, 2,
                               "Discount amount isn't correct")
        self.assertAlmostEqual(line.amount_currency, 1500, 2,
                               "amount currency isn't correct")
