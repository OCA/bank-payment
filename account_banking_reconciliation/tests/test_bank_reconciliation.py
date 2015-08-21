# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#    Copyright (C) 2015 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
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

from openerp.tests import common
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class test_bank_reconciliation(common.TransactionCase):
    def setUp(self):
        super(test_bank_reconciliation, self).setUp()
        self.user_model = self.registry('res.users')
        self.account_model = self.registry('account.account')
        self.journal_model = self.registry('account.journal')
        self.move_model = self.registry('account.move')
        self.move_line_model = self.registry('account.move.line')
        self.reconcile_model = self.registry('bank.acc.rec.statement')

        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        self.account_bank_id = self.account_model.search(
            cr, uid, [('type', '=', 'liquidity')], context=context)[0]

        self.account_supplier_id = self.account_model.search(
            cr, uid, [('type', '=', 'payable')], context=context)[0]

        self.journal_id = self.journal_model.search(
            cr, uid, [('type', '=', 'bank')], context=context)[0]

        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)

        self.move_id = self.move_model.create(
            cr, uid, {
                'journal_id': self.journal_id,
                'date': today,
                'line_id': [
                    (0, 0, {
                        'name': 'Test',
                        'account_id': move_line[0],
                        'debit': move_line[1],
                        'credit': move_line[2],
                    })
                    for move_line in [
                        (self.account_bank_id, 0, 10),
                        (self.account_bank_id, 0, 20),
                        (self.account_bank_id, 0, 30),
                        (self.account_supplier_id, 60, 0),
                    ]
                ]
            }, context=context)

        account_move = self.move_model.browse(
            cr, uid, self.move_id, context=context)

        account_move.button_validate()

        self.reconcile_id = self.reconcile_model.create(
            cr, uid, {
                'account_id': self.account_bank_id,
                'name': 'Test',
                'ending_date': today,
                'ending_balance': 100,
                'starting_balance': 30,
                'ending_balance_in_currency': 100,
                'starting_balance_in_currency': 30,
            }, context=context)

        self.reconcile = self.reconcile_model.browse(
            cr, uid, self.reconcile_id, context=context)

        self.reconcile.refresh_record()

        self.reconcile.refresh()

    def test_one_reconcile_line_per_move_line(self):
        """
        Test that one line of reconciliation is created for
        each account move for the account
        """
        self.assertEqual(len(self.reconcile.credit_move_line_ids), 3)
