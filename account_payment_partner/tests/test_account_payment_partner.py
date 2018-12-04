# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common
from odoo import report


class TestAccountPaymentPartner(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountPaymentPartner, cls).setUpClass()
        cls.journal_bank = cls.env['res.partner.bank'].create({
            'acc_number': 'GB95LOYD87430237296288',
            'partner_id': cls.env.user.company_id.id,
        })
        cls.journal = cls.env['account.journal'].create({
            'name': 'BANK TEST',
            'code': 'TEST',
            'type': 'bank',
            'bank_account_id': cls.journal_bank.id,
        })
        mode_in = cls.env['account.payment.mode'].create({
            'name': 'Payment Mode Inbound',
            'payment_method_id':
                cls.env.ref('account.account_payment_method_manual_in').id,
            'bank_account_link': 'fixed',
            'fixed_journal_id': cls.journal.id,
        })
        method_out = cls.env.ref('account.account_payment_method_manual_out')
        method_out.bank_account_required = True
        cls.mode_out = cls.env['account.payment.mode'].create({
            'name': 'Payment Mode Outbound',
            'payment_method_id': method_out.id,
            'bank_account_link': 'fixed',
            'fixed_journal_id': cls.journal.id,
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'customer': True,
            'customer_payment_mode_id': mode_in.id,
        })
        cls.supplier = cls.env['res.partner'].create({
            'name': 'Test Supplier',
            'supplier': True,
            'supplier_payment_mode_id': cls.mode_out.id,
        })
        cls.supplier_bank = cls.env['res.partner.bank'].create({
            'acc_number': 'GB18BARC20040131665123',
            'partner_id': cls.supplier.id,
        })
        cls.supplier_invoice = cls.env['account.invoice'].create({
            'partner_id': cls.supplier.id,
            'type': 'in_invoice',
        })

    def test_partner_onchange(self):
        customer_invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'type': 'out_invoice',
        })
        customer_invoice._onchange_partner_id()
        self.assertEqual(customer_invoice.payment_mode_id,
                         self.partner.customer_payment_mode_id)

        self.supplier_invoice._onchange_partner_id()
        self.assertEqual(self.supplier_invoice.partner_bank_id,
                         self.supplier_bank)
        vals = {'partner_id': False, 'type': 'out_invoice'}
        invoice = self.env['account.invoice'].new(vals)
        invoice._onchange_partner_id()
        self.assertFalse(invoice.payment_mode_id)
        vals = {'partner_id': False, 'type': 'in_invoice'}
        invoice = self.env['account.invoice'].new(vals)
        invoice._onchange_partner_id()
        self.assertFalse(invoice.partner_bank_id)

    def test_payment_mode_id_change(self):
        self.supplier_invoice.payment_mode_id = self.mode_out.id
        self.supplier_invoice.payment_mode_id_change()
        self.assertEqual(self.supplier_invoice.partner_bank_id,
                         self.supplier_bank)
        self.mode_out.payment_method_id.bank_account_required = False
        self.supplier_invoice.payment_mode_id = self.mode_out.id
        self.supplier_invoice.payment_mode_id_change()
        self.assertFalse(self.supplier_invoice.partner_bank_id)
        self.supplier_invoice.payment_mode_id = False
        self.supplier_invoice.payment_mode_id_change()
        self.assertFalse(self.supplier_invoice.partner_bank_id)

    def test_print_report(self):
        self.env['account.invoice.line'].create({
            'invoice_id': self.supplier_invoice.id,
            'name': 'Product Text',
            'price_unit': 10.0,
            'account_id': self.env.ref('l10n_generic_coa.1_conf_o_income').id,
        })
        self.supplier_invoice.action_invoice_open()
        self.assertEqual(
            self.supplier_invoice.move_id.line_ids[0].payment_mode_id,
            self.supplier_invoice.payment_mode_id)
        (res, _) = report.render_report(
            self.env.cr, self.env.uid,
            [self.supplier_invoice.id], 'account.report_invoice', {})
        self.assertRegexpMatches(res, self.supplier_bank.acc_number)
        self.supplier_invoice.partner_bank_id = False
        self.supplier_invoice.payment_mode_id\
            .show_bank_account_from_journal = True
        (res, _) = report.render_report(
            self.env.cr, self.env.uid,
            [self.supplier_invoice.id], 'account.report_invoice', {})
        self.assertRegexpMatches(res, self.journal_bank.acc_number)
        payment_mode = self.supplier_invoice.payment_mode_id
        self.supplier_invoice.payment_mode_id = False
        payment_mode.bank_account_link = 'variable'
        payment_mode.variable_journal_ids = [
            (6, 0, [self.journal.id])]
        self.supplier_invoice.payment_mode_id = payment_mode.id
        self.supplier_invoice.payment_mode_id_change()
        (res, _) = report.render_report(
            self.env.cr, self.env.uid,
            [self.supplier_invoice.id], 'account.report_invoice', {})
        self.assertRegexpMatches(
            res, self.journal_bank.acc_number)
