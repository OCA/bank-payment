# -*- coding: utf-8 -*-
# Copyright 2017 Compassion CH (http://www.compassion.ch)
# @author: Marco Monzione <marco.mon@windowslive.com>, Emanuel Cino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import tools, fields
from odoo.tests import TransactionCase
from odoo.modules.module import get_resource_path


class TestPaymentCancel(TransactionCase):
    def _load(self, module, *args):
        tools.convert_file(
            self.cr, 'account_asset',
            get_resource_path(module, *args),
            {}, 'init', False, 'test', self.registry._assertion_report)

    def test_free_invoice(self):
        self._load('account', 'test', 'account_minimal_test.xml')
        journal = self.env['account.journal'].search([
            ('code', '=', 'TEXJ')], limit=1)
        account = self.env['account.account'].search([
            ('code', '=', 'X1012')], limit=1)
        product = self.env.ref('product.product_product_24')
        account_line = self.env['account.account'].search([
            ('code', '=', 'X2020')], limit=1)

        # Create invoice
        invoice = self.env['account.invoice'].create({
            'journal_id': journal.id,
            'currency_id': self.env.ref('base.USD').id,
            'account_id': account.id,
            'type': 'in_invoice',
            'partner_id': self.env.ref('base.res_partner_address_31').id,
            'date_invoice': fields.Datetime.now(),
            'invoice_line_ids': [(0, 0, {
                'product_id': product.id,
                'name': product.name,
                'account_id': account_line.id,
                'quantity': 1,
                'price_unit': product.standard_price
            })]
        })
        invoice.action_invoice_open()
        payorder_id = invoice.create_account_payment_line().get('res_id')
        payment_order = self.env['account.payment.order'].browse(payorder_id)
        payment_order.journal_id = journal

        # Confirm payment order
        payment_order.draft2open()
        # Generate payment file
        payment_order.open2generated()
        # File successfully uploaded
        payment_order.generated2uploaded()

        # The invoice should be paid
        self.assertEquals(invoice.state, 'paid')

        # Make journal cancellable
        journal.update_posted = True
        wizard = self.env['account.invoice.free'].with_context(
            active_ids=invoice.ids).create({})
        wizard.invoice_free()

        # Test if the move related to the invoice are deleted after the invoice
        # is freed.
        account_move = self.env['account.move'].search(
            [('payment_order_id', '=', payment_order.id)])

        self.assertFalse(account_move)

        # Test if the order is in cancel state.
        self.assertEqual(payment_order.state, 'cancel')

        # Test if the invoice is in open state.
        self.assertEqual(invoice.state, 'open')
