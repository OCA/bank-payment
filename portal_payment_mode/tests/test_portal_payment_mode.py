# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Sergio Teruel
# Copyright 2015 Tecnativa - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestPortalPaymentMode(TransactionCase):

    def setUp(self):
        super(TestPortalPaymentMode, self).setUp()
        self.partner = self.env.ref('portal.partner_demo_portal')
        self.bank = self.env['res.partner.bank'].create({
            'state': 'bank',
            'bank_name': 'Test bank',
            'acc_number': '1234567890'})
        self.journal = self.env['account.journal'].create({
            'name': 'Test journal',
            'code': 'TEST',
            'type': 'general'})
        self.payment_mode = self.env['account.payment.mode'].create({
            'name': 'Test Payment Mode',
            'journal': self.journal.id,
            'bank_id': self.bank.id,
            'bank_account_link': 'variable',
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_in').id,
            'sale_ok': True,
        })
        self.account = self.env['account.account'].create({
            'name': 'Test account',
            'code': 'TESTACC',
            'user_type_id': self.env.ref(
                'account.data_account_type_receivable').id,
            'reconcile': True,
        })
        self.journal = self.env['account.journal'].create({
            'name': 'TEST JOURNAL',
            'code': 'TSTJRNL',
            'type': 'sale',
        })
        vals_invoice = {
            'partner_id': self.partner.id,
            'account_id': self.account.id,
            'journal_id': self.journal.id,
            'payment_mode_id': self.payment_mode.id,
            'invoice_line': [(0, 0, {
                'name': 'test',
                'account_id': self.account.id,
                'price_unit': 100.00,
                'quantity': 1
            })],
        }
        self.invoice = self.env['account.invoice'].create(vals_invoice)
        self.invoice.invoice_validate()

    def test_access_invoice(self):
        user_portal = self.env['res.users'].search(
            [('partner_id', '=', self.partner.id)])
        self.assert_(self.invoice.sudo(user_portal).payment_mode_id)
