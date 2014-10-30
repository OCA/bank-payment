# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
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
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


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
                 'discount_amount': 500,
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
        today = datetime.now()
        date = today.strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice = create_simple_invoice(self, date)
        workflow.trg_validate(self.uid, 'account.invoice', invoice.id,
                              'invoice_open', self.cr)
        payment_order_create_obj = self.env['payment.order.create']
        account_payment_id = self.ref('account_payment.payment_order_1')
        payment_order_create = payment_order_create_obj.create(
            {'duedate': date,
             'cash_discount_date': True,
             'populate_results': True})
        self.context.update({'active_id': account_payment_id})
        res = payment_order_create.with_context(self.context).search_entries()
        payment_order_create.entries = res['context']['line_ids']
        payment_order_create.with_context(self.context).create_payment()
        account_payment = self.env['payment.order']\
            .browse([account_payment_id])
        self.assertEqual(len(account_payment.line_ids.ids), 1,
                         "Number of line isn't correct")
        line = account_payment.line_ids[0]
        self.assertAlmostEqual(line.discount_amount, 500, 2,
                               "Discount amount isn't correct")
        self.assertAlmostEqual(line.amount_currency, 1500, 2,
                               "amount currency isn't correct")
