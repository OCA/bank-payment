# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Marco Monzione <marco.mon@windowslive.com>, Emanuel Cino
#
#    The licence is in the file __manifest__.py
#
##############################################################################
from odoo.tests import TransactionCase
from odoo import fields


class TestPaymentCancel(TransactionCase):

    def setUp(self):
        super(TestPaymentCancel, self).setUp()

        self.invoice_name = 'test invoice pain000'
        self.invoice_line_name = 'test invoice line pain000'
        self.order_name = '2017/1013'
        self.journal_name = '2017/1013'
        self.payment_line_name = 'Ltest'

        # Create invoice
        self.invoice = self.env['account.invoice'].create({
            'company_id': self.env['res.company'].search([
                ('name', '=', 'YourCompany')
            ]).id,
            'move_name': self.invoice_name,
            'journal_id': self.env['account.journal'].search([
                ('name', '=', self.journal_name)
            ]).id,
            'currency_id': self.env['res.currency'].search([
                ('name', '=', 'CHF')
            ]).id,
            'account_id': self.env['account.account'].search([
                ('code', '=', '1100')
            ]).id,
            'type': 'in_invoice',
            'partner_id': self.env['res.partner'].search([
                ('name', '=', 'pain000 test')
            ]).id,
            'date_invoice': fields.Datetime.now(),
            'partner_bank_id': self.env['res.partner.bank'].search([
                ('acc_number', '=', '25-9778-2')
            ]).id,
            'payment_mode_id': self.env['account.payment.mode'].search([
                ('name', '=', 'DD')
            ]).id
        })

        # Add an invoice line to our invoice.
        self.env['account.invoice.line'].create({
            'account_id': self.env['account.account'].search([
                ('code', '=', '3200')
            ]).id,
            'name': 'test invoice line pain000',
            'price_unit': 600.0,
            'quantity': 1.0,
            'product_id': self.env['product.product'].search([
                ('default_code', '=', 'E-COM09')
            ]).id,
            'invoice_id': self.invoice.id

        })

        # Validate the invoice
        self.invoice.action_invoice_open()

        # Create a payment order
        action = self.invoice.create_account_payment_line()
        payment_order_id = action['res_id']

        payment_order = self.env['account.payment.order'].search(
            [('id', '=', payment_order_id)])

        partner_bank = self.env['account.journal'].search(
            [('name', '=', self.journal_name)])

        bank = self.env['account.journal'].search([('name', '=', 'Bank')])

        payment_order.name = self.order_name
        bank.update_posted = True

        payment_order.journal_id = partner_bank.id
        # Confirm payment order
        payment_order.draft2open()
        # Generate payment file
        payment_order.open2generated()
        # File successfully uploaded
        payment_order.generated2uploaded()

        payment_line = self.env['bank.payment.line'].search(
            [('order_id', '=', payment_order.id)])

        payment_line.name = self.payment_line_name

    def test_free_invoice(self):
        self._invoice_free()

        # Test if the move related to the invoice are deleted after the invoice
        # is freed.
        payment_order = self.env['account.payment.order'].search(
            [('name', '=', self.order_name)])
        account_move = self.env['account.move'].search(
            [('payment_order_id', '=', payment_order.id)])

        self.assertFalse(account_move)

        # Test if the order is in cancel state.
        payment_order = self.env['account.payment.order'].search(
            [('name', '=', self.order_name)])

        self.assertEqual(payment_order.state, 'cancel')

        # Test if the invoice is in open state.
        self.assertEqual(self.invoice.state, 'open')

    def _invoice_free(self):
        invoice = self.env['account.invoice'].search(
            [('move_name', '=', self.invoice_name)])

        free_wizard = self.env['account.invoice.free'].with_context(
            active_ids=invoice.ids).create({})
        free_wizard.invoice_free()
