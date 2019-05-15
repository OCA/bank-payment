# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.account.tests.account_test_users import AccountingTestCase


class TestCancelInvoice(AccountingTestCase):

    def setUp(self):
        super(TestCancelInvoice, self).setUp()
        self.tax = self.env['account.tax'].create({
            'name': 'Tax 10.0',
            'amount': 10.0,
            'amount_type': 'fixed',
        })
        self.analytic_account = self.env['account.analytic.account'].create({
            'name': 'test account',
        })

        # Should be changed by automatic on_change later
        self.invoice_account = self.env['account.account'].search([
            ('user_type_id', '=', self.env.ref(
                'account.data_account_type_receivable').id)
        ], limit=1).id
        self.invoice_line_account = self.env['account.account'].search([
            ('user_type_id', '=', self.env.ref(
                'account.data_account_type_expenses').id)
        ], limit=1).id

    def _create_simple_invoice(self):
        self.invoice = self.env['account.invoice'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'account_id': self.invoice_account,
            'type': 'in_invoice',
        })

        self.env['account.invoice.line'].create({
            'product_id': self.env.ref('product.product_product_4').id,
            'quantity': 1.0,
            'price_unit': 100.0,
            'invoice_id': self.invoice.id,
            'name': 'product that cost 100',
            'account_id': self.invoice_line_account,
            'invoice_line_tax_ids': [(6, 0, [self.tax.id])],
            'account_analytic_id': self.analytic_account.id,
        })

    def test_cancel_invoice(self):
        # I check if created invoice isn't linked with a payment line
        self._create_simple_invoice()
        self.invoice.action_invoice_open()
        journal = self.invoice.journal_id
        journal.update_posted = True

        payment_lines = self.invoice.get_payment_line_linked()
        self.assertTrue(len(payment_lines) == 0,
                        "Invoice is linked with a payment line")
        # I click on cancel invoice button
        res = self.invoice.action_invoice_cancel()
        # I check if the wizard is correctly instantiated
        self.assertFalse(isinstance(res, dict), "wizard action is returned")
        # I check if invoice is cancelled
        self.assertEqual(
            self.invoice.state,
            'cancel',
            'Invoice isn\'t cancelled'
        )

    def test_payment_cancel_invoice(self):
        """
        Create a supplier invoice
        Validate that invoice
        Create a payment line linked to that invoice
        Try to cancel the invoice
        Check the wizard to validate cancellation is launched
        Validate the cancellation
        Check invoice state
        :return:
        """
        self._create_simple_invoice()
        journal = self.invoice.journal_id
        journal.update_posted = True

        self.invoice.action_invoice_open()
        payment_order_create_obj = self.env[
            'account.invoice.payment.line.multi']

        context = self.env.context.copy()
        context.update({
            'active_ids': [self.invoice.id],
            'active_model': 'account.invoice'
        })
        payment_order_create = payment_order_create_obj.with_context(
            context).create({})
        payment_order_create.run()
        # I check if created invoice is linked with a payment line
        payment_lines = self.invoice.get_payment_line_linked()
        self.assertTrue(len(payment_lines) > 0,
                        "Invoice isn't on a payment line")
        # I click on cancel invoice button
        res = self.invoice.action_invoice_cancel()
        # I check if the wizard is correctly instantiated
        self.assertTrue(isinstance(res, dict), "Not return wizard action")
        ctx = res.get('context')
        wizard_id = res.get('res_id')
        wizard_obj = self.env['validate.invoice.cancel']
        wizard = wizard_obj.browse([wizard_id])[0]
        # click on force cancel button
        wizard.with_context(ctx).validate_cancel()
        # I check if invoice is cancelled
        self.assertEqual(
            self.invoice.state,
            'cancel',
            'Invoice isn\'t cancelled'
        )
