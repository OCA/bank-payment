# Copyright 2013-2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields
from odoo.tests import common


class TestAccountPaymentPurchase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountPaymentPurchase, cls).setUpClass()
        cls.journal = cls.env['account.journal'].create(
            {'name': 'Test journal',
             'code': 'TEST',
             'type': 'general'})
        cls.payment_mode = cls.env['account.payment.mode'].create(
            {'name': 'Test payment mode',
             'fixed_journal_id': cls.journal.id,
             'bank_account_link': 'variable',
             'payment_method_id': cls.env.ref(
                 'account.account_payment_method_manual_in').id})
        cls.partner = cls.env['res.partner'].create(
            {'name': 'Test partner',
             'supplier_payment_mode_id': cls.payment_mode.id})
        cls.bank = cls.env['res.partner.bank'].create(
            {'bank_name': 'Test bank',
             'acc_number': '1234567890',
             'partner_id': cls.partner.id,
             })
        cls.bank2 = cls.env['res.partner.bank'].create(
            {'bank_name': 'Test bank #2',
             'acc_number': '0123456789',
             'partner_id': cls.partner.id,
             })
        cls.uom_id = cls.env.ref('uom.product_uom_unit').id
        cls.mto_product = cls.env['product.product'].create(
            {'name': 'Test buy product',
             'uom_id': cls.uom_id,
             'uom_po_id': cls.uom_id,
             'seller_ids': [(0, 0, {'name': cls.partner.id})]})
        cls.purchase = cls.env['purchase.order'].create(
            {'partner_id': cls.partner.id,
             'payment_mode_id': cls.payment_mode.id,
             'order_line': [(0, 0, {'name': 'Test line',
                                    'product_qty': 1.0,
                                    'product_id': cls.mto_product.id,
                                    'product_uom': cls.uom_id,
                                    'date_planned': fields.Date.today(),
                                    'price_unit': 1.0})]})

    def test_onchange_partner_id_purchase_order(self):
        self.purchase.onchange_partner_id()
        self.assertEqual(self.purchase.payment_mode_id, self.payment_mode)

    def test_purchase_order_invoicing(self):
        self.purchase.button_confirm()

        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'purchase_id': self.purchase.id,
            'account_id': self.partner.property_account_payable_id.id,
        })
        invoice.purchase_order_change()
        self.assertEqual(
            self.purchase.invoice_ids[0].payment_mode_id, self.payment_mode)

    def test_from_purchase_order_invoicing(self):
        # Test payment mode
        product = self.env['product.product'].create(
            {'name': 'Test product',
             })
        self.purchase.order_line[0].product_id = product.id
        self.purchase.button_confirm()

        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'purchase_id': self.purchase.id,
            'account_id': self.partner.property_account_payable_id.id,
        })
        invoice.purchase_order_change()
        self.assertEqual(invoice.payment_mode_id, self.payment_mode)
        purchase2 = self.purchase.copy()
        payment_mode2 = self.payment_mode.copy()
        purchase2.payment_mode_id = payment_mode2.id
        purchase2.button_confirm()

        invoice.purchase_id = purchase2.id
        result = invoice.purchase_order_change()
        self.assertEqual(result['warning']['title'], 'Warning')

    def test_from_purchase_order_invoicing_bank(self):
        # Test patner_bank
        product = self.env['product.product'].create(
            {'name': 'Test product',
             })
        self.purchase.order_line[0].product_id = product.id
        self.purchase.payment_mode_id = False
        self.purchase.supplier_partner_bank_id = self.bank.id
        self.purchase.button_confirm()

        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'purchase_id': self.purchase.id,
            'account_id': self.partner.property_account_payable_id.id,
        })
        # Avoid bank company from default_get method
        invoice.partner_bank_id = False
        invoice.purchase_order_change()
        self.assertEqual(invoice.partner_bank_id, self.bank)
        purchase2 = self.purchase.copy()
        purchase2.supplier_partner_bank_id = self.bank2.id
        purchase2.button_confirm()

        invoice.purchase_id = purchase2.id
        result = invoice.purchase_order_change()
        self.assertEqual(result['warning']['title'], 'Warning')
