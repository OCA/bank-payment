# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
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
        self.payment_mode = self.env['payment.mode'].create({
            'name': 'Test Payment Mode',
            'journal': self.journal.id,
            'bank_id': self.bank.id,
            'type': self.env.ref(
                'account_banking_payment_export.manual_bank_tranfer').id,
            'sale_ok': True,
        })
        vals_invoice = {
            'partner_id': self.partner.id,
            'account_id': self.env.ref('account.a_sale').id,
            'journal_id': self.env.ref('account.sales_journal').id,
            'payment_mode_id': self.payment_mode.id,
            'invoice_line': [(0, 0, {
                'name': 'test',
                'account_id': self.env.ref('account.a_sale').id,
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
