# -*- coding: utf-8 -*-
# Copyright 2018 Sunflower IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import time
from lxml import etree
from openerp.tools import float_compare
from openerp.tests import common
from datetime import datetime


class TestSCT(common.TransactionCase):

    def setUp(self):
        super(TestSCT, self).setUp()
        self.main_company = self.env.ref('base.main_company')
        self.payment_mode = self.env.ref(
            'account_banking_sepa_credit_transfer.'
            'sepa_credit_transfer_mode'
        )
        year = datetime.now().strftime('%Y')
        fiscalyear_id = self.env['account.fiscalyear'].create({
            'name': year,
            'code': year,
            'company_id': self.main_company.id,
            'date_start': '%s-01-01' % year,
            'date_stop': '%s-12-31' % year,
        })
        fiscalyear_id.create_period()

    def test_with_or_without_bic(self):
        invoice = self.env.ref('account.invoice_3')
        invoice.signal_workflow('invoice_open')
        move_line = invoice.move_id.line_id[0]
        payment_order = self.env.ref('account_payment.payment_order_1')
        partner_bank = invoice.partner_id.bank_ids[0]
        for bic in [None, 'NLINGB4U']:
            partner_bank.write({
                'state': 'iban',
                'acc_number': 'NL08INGB0000000555',
                'bank_bic': bic,
            })
            payment_order.write({
                'mode': self.payment_mode.id,
                'line_ids': [(0, False, {
                    'name': '/' if not bic else bic,
                    'move_line_id': move_line.id,
                    'communication': '/',
                    'partner_id': invoice.partner_id.id,
                    'currency': invoice.currency_id.id,
                    'amount_currency': move_line.amount_residual_currency,
                    'bank_id': partner_bank.bank.id
                })]
            })
            payment_order.action_open()
            wizard = self.env['banking.export.sepa.wizard'].with_context({
                'active_ids': [payment_order.id]
            }).create({})
            wizard.create_sepa()
            content = base64.b64decode(wizard.file)
            if bic:
                self.assertTrue('NLINGB4U' in content)
            else:
                self.assertFalse('NLINGB4U' in content)


