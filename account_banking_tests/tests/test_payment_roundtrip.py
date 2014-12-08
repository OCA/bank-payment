# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Therp BV (<http://therp.nl>)
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
from datetime import datetime
from openerp.tests.common import SingleTransactionCase
from openerp import netsvc


class TestPaymentRoundtrip(SingleTransactionCase):

    def assert_payment_order_state(self, expected):
        """
        Check that the state of our payment order is
        equal to the 'expected' parameter
        """
        state = self.registry('payment.order').read(
            self.cr, self.uid, self.payment_order_id, ['state'])['state']
        assert state == expected, \
            'Payment order does not go into state \'%s\'.' % expected

    def assert_invoices_state(self, expected):
        """
        Check that the state of our invoices is
        equal to the 'expected' parameter
        """
        for invoice in self.registry('account.invoice').read(
                self.cr, self.uid, self.invoice_ids, ['state']):
            assert invoice['state'] == expected, \
                'Invoice does not go into state \'%s\'' % expected

    def setup_company(self, reg, cr, uid):
        """
        Set up a company with a bank account and configure the
        current user to work with that company
        """
        data_model = reg('ir.model.data')
        self.country_id = data_model.get_object_reference(
            cr, uid, 'base', 'nl')[1]
        self.currency_id = data_model.get_object_reference(
            cr, uid, 'base', 'EUR')[1]
        self.bank_id = reg('res.bank').create(
            cr, uid,
            {
                'name': 'ING Bank',
                'bic': 'INGBNL2A',
                'country': self.country_id,
            })
        self.company_id = reg('res.company').create(
            cr, uid,
            {
                'name': '_banking_addons_test_company',
                'currency_id': self.currency_id,
                'country_id': self.country_id,
            })
        self.partner_id = reg('res.company').read(
            cr, uid, self.company_id, ['partner_id'])['partner_id'][0]
        self.partner_bank_id = reg('res.partner.bank').create(
            cr, uid,
            {
                'state': 'iban',
                'acc_number': 'NL08INGB0000000555',
                'bank': self.bank_id,
                'bank_bic': 'INGBNL2A',
                'partner_id': self.partner_id,
                'company_id': self.company_id,
            })
        reg('res.users').write(
            cr, uid, [uid],
            {'company_ids': [(4, self.company_id)]})
        reg('res.users').write(
            cr, uid, [uid],
            {'company_id': self.company_id})

    def setup_chart(self, reg, cr, uid):
        """
        Set up the configurable chart of accounts and create periods
        """
        data_model = reg('ir.model.data')
        chart_setup_model = reg('wizard.multi.charts.accounts')
        chart_template_id = data_model.get_object_reference(
            cr, uid, 'account', 'configurable_chart_template')[1]
        chart_values = {
            'company_id': self.company_id,
            'currency_id': self.currency_id,
            'chart_template_id': chart_template_id
        }
        chart_values.update(
            chart_setup_model.onchange_chart_template_id(
                cr, uid, [], 1)['value'])
        chart_setup_id = chart_setup_model.create(
            cr, uid, chart_values)
        chart_setup_model.execute(
            cr, uid, [chart_setup_id])
        year = datetime.now().strftime('%Y')
        fiscalyear_id = reg('account.fiscalyear').create(
            cr, uid,
            {
                'name': year,
                'code': year,
                'company_id': self.company_id,
                'date_start': '%s-01-01' % year,
                'date_stop': '%s-12-31' % year,
            })
        reg('account.fiscalyear').create_period(
            cr, uid, [fiscalyear_id])

    def setup_payables(self, reg, cr, uid, context=None):
        """
        Set up suppliers and invoice them. Check that the invoices
        can be validated properly.
        """
        partner_model = reg('res.partner')
        supplier1 = partner_model.create(
            cr, uid, {
                'name': 'Supplier 1',
                'supplier': True,
                'country_id': self.country_id,
                'bank_ids': [
                    (0, False, {
                        'state': 'iban',
                        'acc_number': 'NL42INGB0000454000',
                        'bank': self.bank_id,
                        'bank_bic': 'INGBNL2A',
                    })
                ],
            }, context=context)
        supplier2 = partner_model.create(
            cr, uid, {
                'name': 'Supplier 2',
                'supplier': True,
                'country_id': self.country_id,
                'bank_ids': [
                    (0, False, {
                        'state': 'iban',
                        'acc_number': 'NL86INGB0002445588',
                        'bank': self.bank_id,
                        'bank_bic': 'INGBNL2A',
                    })
                ],
            }, context=context)
        self.payable_id = reg('account.account').search(
            cr, uid, [
                ('company_id', '=', self.company_id),
                ('code', '=', '120000')])[0]
        expense_id = reg('account.account').search(
            cr, uid, [
                ('company_id', '=', self.company_id),
                ('code', '=', '123000')])[0]
        invoice_model = reg('account.invoice')
        values = {
            'type': 'in_invoice',
            'partner_id': supplier1,
            'account_id': self.payable_id,
            'invoice_line': [
                (
                    0,
                    False,
                    {
                        'name': 'Purchase 1',
                        'price_unit': 100.0,
                        'quantity': 1,
                        'account_id': expense_id,
                    }
                )
            ],
            'reference_type': 'none',
            'supplier_invoice_number': 'INV1',
        }
        self.invoice_ids = [
            invoice_model.create(
                cr, uid, values,
                context={
                    'type': 'in_invoice',
                })
        ]
        values.update({
            'partner_id': supplier2,
            'name': 'Purchase 2',
            'reference_type': 'structured',
            'supplier_invoice_number': 'INV2',
            'reference': 'STR2',
        })
        self.invoice_ids.append(
            invoice_model.create(
                cr, uid, values, context={
                    'type': 'in_invoice'}))
        wf_service = netsvc.LocalService('workflow')
        for invoice_id in self.invoice_ids:
            wf_service.trg_validate(
                uid, 'account.invoice', invoice_id, 'invoice_open', cr)
        self.assert_invoices_state('open')

    def setup_payment_config(self, reg, cr, uid):
        """
        Configure an additional account and journal for payments
        in transit and configure a payment mode with them.
        """
        account_parent_id = reg('account.account').search(
            cr, uid,
            [
                ('company_id', '=', self.company_id),
                ('parent_id', '=', False)
            ])[0]
        user_type = reg('ir.model.data').get_object_reference(
            cr, uid, 'account', 'data_account_type_liability')[1]
        transfer_account_id = reg('account.account').create(
            cr, uid,
            {
                'company_id': self.company_id,
                'parent_id': account_parent_id,
                'code': 'TRANS',
                'name': 'Transfer account',
                'type': 'other',
                'user_type': user_type,
                'reconcile': True,
            })
        transfer_journal_id = reg('account.journal').search(
            cr, uid, [
                ('company_id', '=', self.company_id),
                ('code', '=', 'MISC')
            ])[0]
        self.bank_journal_id = reg('account.journal').search(
            cr, uid, [
                ('company_id', '=', self.company_id),
                ('type', '=', 'bank')
            ])[0]
        payment_mode_type_id = reg('ir.model.data').get_object_reference(
            cr, uid, 'account_banking_sepa_credit_transfer',
            'export_sepa_sct_001_001_03')[1]
        self.payment_mode_id = reg('payment.mode').create(
            cr, uid,
            {
                'name': 'SEPA Mode',
                'bank_id': self.partner_bank_id,
                'journal': self.bank_journal_id,
                'company_id': self.company_id,
                'transfer_account_id': transfer_account_id,
                'transfer_journal_id': transfer_journal_id,
                'type': payment_mode_type_id,
            })

    def setup_payment(self, reg, cr, uid):
        """
        Create a payment order with the invoices' payable move lines.
        Check that the payment order can be confirmed.
        """
        self.payment_order_id = reg('payment.order').create(
            cr, uid,
            {
                'reference': 'PAY001',
                'mode': self.payment_mode_id,
            })
        context = {'active_id': self.payment_order_id}
        entries = reg('account.move.line').search(
            cr, uid,
            [
                ('company_id', '=', self.company_id),
                ('account_id', '=', self.payable_id),
            ])
        self.payment_order_create_id = reg('payment.order.create').create(
            cr, uid,
            {
                'entries': [(6, 0, entries)],
            },
            context=context)
        reg('payment.order.create').create_payment(
            cr, uid, [self.payment_order_create_id], context=context)

        # Check if payment lines are created with the correct reference
        self.assertTrue(
            reg('payment.line').search(
                cr, uid,
                [
                    ('move_line_id.invoice', '=', self.invoice_ids[0]),
                    ('communication', '=', 'INV1'),
                    ('state', '=', 'normal'),
                ],
                context=context),
            'No payment line created from invoice 1 or with the wrong '
            'communication')
        self.assertTrue(
            reg('payment.line').search(
                cr, uid,
                [
                    ('move_line_id.invoice', '=', self.invoice_ids[1]),
                    ('communication', '=', 'STR2'),
                    ('state', '=', 'structured'),
                ],
                context=context),
            'No payment line created from invoice 2 or with the wrong '
            'communication')

        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(
            uid, 'payment.order', self.payment_order_id, 'open', cr)
        self.assert_payment_order_state('open')

    def export_payment(self, reg, cr, uid):
        """
        Call the SEPA export wizard on the payment order
        and check that the payment order and related invoices'
        states are moved forward afterwards
        """
        export_model = reg('banking.export.sepa.wizard')
        export_id = export_model.create(
            cr, uid,
            {
                'msg_identification': 'EXP001'
            },
            context={'active_ids': [self.payment_order_id]})
        export_model.create_sepa(
            cr, uid, [export_id])
        export_model.save_sepa(
            cr, uid, [export_id])
        self.assert_payment_order_state('sent')
        self.assert_invoices_state('paid')

    def setup_bank_statement(self, reg, cr, uid):
        """
        Create a bank statement with a single line. Call the reconciliation
        wizard to match the line with the open payment order. Confirm the
        bank statement. Check if the payment order is done.
        """
        statement_model = reg('account.bank.statement')
        line_model = reg('account.bank.statement.line')
        wizard_model = reg('banking.transaction.wizard')
        statement_id = statement_model.create(
            cr, uid,
            {
                'name': 'Statement',
                'journal_id': self.bank_journal_id,
                'balance_end_real': -200.0,
                'period_id': reg('account.period').find(cr, uid)[0]
            })
        line_id = line_model.create(
            cr, uid,
            {
                'name': 'Statement line',
                'statement_id': statement_id,
                'amount': -200.0,
                'account_id': self.payable_id,
            })
        wizard_id = wizard_model.create(
            cr, uid, {'statement_line_id': line_id})
        wizard_model.write(
            cr, uid, [wizard_id], {
                'manual_payment_order_id': self.payment_order_id})
        statement_model.button_confirm_bank(cr, uid, [statement_id])
        self.assert_payment_order_state('done')

    def check_reconciliations(self, reg, cr, uid):
        """
        Check if the payment order has any lines and that
        the transit move lines of those payment lines are
        reconciled by now.
        """
        payment_order = reg('payment.order').browse(
            cr, uid, self.payment_order_id)
        assert payment_order.line_ids, 'Payment order has no payment lines'
        for line in payment_order.line_ids:
            assert line.transit_move_line_id, \
                'Payment order has no transfer move line'
            assert line.transit_move_line_id.reconcile_id, \
                'Transfer move line on payment line is not reconciled'

    def test_payment_roundtrip(self):
        reg, cr, uid, = self.registry, self.cr, self.uid
        # Tests fail if admin does not have the English language
        reg('res.users').write(cr, uid, uid, {'lang': 'en_US'})
        self.setup_company(reg, cr, uid)
        self.setup_chart(reg, cr, uid)
        self.setup_payables(reg, cr, uid)
        self.setup_payment_config(reg, cr, uid)
        self.setup_payment(reg, cr, uid)
        self.export_payment(reg, cr, uid)
        self.setup_bank_statement(reg, cr, uid)
        self.check_reconciliations(reg, cr, uid)
