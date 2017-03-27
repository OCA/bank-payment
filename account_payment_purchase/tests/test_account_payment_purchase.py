# -*- coding: utf-8 -*-
# (c) 2013-2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import SavepointCase


class TestAccountPaymentPurchase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountPaymentPurchase, cls).setUpClass()

        # ENVIRONMENTS
        cls.partner_bank = cls.env['res.partner.bank']
        cls.bank = cls.env['res.bank']
        cls.journal = cls.env['account.journal']
        cls.bank_journal = cls.env['account.journal']
        cls.payment_mode = cls.env['account.payment.mode']
        cls.partner = cls.env['res.partner']
        cls.purchase = cls.env['purchase.order']
        cls.product = cls.env['product.product']
        cls.rule = cls.env['procurement.rule']
        cls.procurement_order = cls.env['procurement.order']
        cls.stock_location = cls.env['stock.location']
        cls.stock_warehouse = cls.env['stock.warehouse']
        cls.account_invoice = cls.env['account.invoice']
        cls.payment_mode_type = cls.env['account.payment']
        cls.sepa_ct = cls.env['account.payment.method']

        # Create an IBAN bank account and its journal
        cls.bank = cls.bank.create({'name': 'ING', 'bic': 'BBRUBEBB'})

        cls.bank_journal = cls.bank_journal.create({
            'name': 'BE48363523682327',
            'type': 'bank',
            'bank_acc_number': 'BE48363523682327',
            'bank_id': cls.bank.id,
        })

        # INSTANCES

        # payment type
        cls.sepa_ct = cls.sepa_ct.create({
            'name': 'SEPA Credit Transfer',
            'code': 'sepa_ct',
            'payment_type': 'outbound'
        })

        cls.payment_mode = cls.payment_mode.create({
            'name': 'Credit Transfer to Suppliers',
            'bank_account_link': 'variable',
            'payment_method_id': cls.sepa_ct.id,
            'purchase_ok': True
        })

        # partner & bank
        cls.partner = cls.partner.search([
            ('name', 'ilike', 'asustek'),
            ('supplier', '=', True)], limit=1)
        cls.partner_2 = cls.partner.search([
            ('name', 'not ilike', 'asustek'),
            ('supplier', '=', True)], limit=1)
        cls.partner.write({
            'supplier_payment_mode_id': cls.payment_mode.id,
        })

        cls.bank_partner = cls.partner_bank.create(
            {'bank_name': 'Test bank',
             'acc_number': '1234567890'})
        cls.bank_partner.create({'acc_type': 'iban',
                                 'partner_id': cls.partner.id,
                                 'acc_number': 'FR39103123456719'
                                 })

        # journal
        cls.journal = cls.journal.create(
            {'name': 'Test journal',
             'code': 'TEST',
             'type': 'general'})
        cls.payment_mode_type = cls.payment_mode_type.create({
            'journal_id': cls.bank_journal.id,
            'payment_method_id': cls.sepa_ct.id,
            'payment_type': 'outbound',
            'payment_date': '2015-04-28',
            'amount': 50,
            'currency_id': cls.env.ref("base.EUR").id,
            'partner_id': cls.partner.id,
            'partner_type': 'supplier',
        })
        cls.purchase = cls.purchase.create(
            {'partner_id': cls.partner_2.id})

    def test_onchange_partner_id_purchase_order(self):
        # assert that bank and payment mode are not setted
        self.assertEqual(self.purchase.payment_mode_id.id, False)
        self.assertEqual(self.purchase.supplier_partner_bank_id.id, False)

        # change partner
        self.purchase.partner_id = self.partner.id
        self.purchase.onchange_partner_id()

        # assert that bank and payment are setted
        self.assertEqual(len(self.purchase.supplier_partner_bank_id), 1)
        self.assertTrue(self.purchase.supplier_partner_bank_id.id
                        in self.partner.bank_ids.ids)
        self.assertEqual(len(self.purchase.payment_mode_id), 1)
        self.assertEqual(self.purchase.payment_mode_id.id,
                         self.payment_mode.id)

    def test_purchase_order_invoicing(self):

        # set partner with good payment method
        self.purchase.partner_id = self.partner.id
        self.purchase.onchange_partner_id()

        self.purchase.button_confirm()
        self.assertEqual(self.purchase.state, u'purchase')
        self.invoice = self.account_invoice.create({
            'type': 'in_invoice',
            'partner_id': self.purchase.partner_id.id,
            'purchase_id': self.purchase.id,
            'account_id':
                self.purchase.partner_id.property_account_payable_id.id,
        })
        self.invoice._onchange_partner_id()
        self.assertEqual(len(self.invoice), 1)
        self.assertEqual(len(self.invoice.payment_mode_id), 1)
        self.assertEqual(self.invoice.payment_mode_id.id, self.payment_mode.id)
        self.assertTrue(self.purchase.supplier_partner_bank_id.id
                        in self.partner.bank_ids.ids)

    def test_procurement_buy_payment_mode(self):
        mto_product = self.product.create(
            {'name': 'Test buy product',
             'type': 'product',
             'seller_ids': [(0, 0, {'name': self.partner.id})]})
        route = self.env.ref('purchase.route_warehouse0_buy')
        rule = self.rule.search(
            [('route_id', '=', route.id)], limit=1)
        procurement_order = self.procurement_order.create(
            {'product_id': mto_product.id,
             'rule_id': rule.id,
             'location_id': self.stock_location.search([], limit=1).id,
             'warehouse_id': self.stock_warehouse.search(
                 [], limit=1).id,
             'product_qty': 1,
             'product_uom': mto_product.uom_id.id,
             'name': 'Procurement order test'})
        procurement_order.run()
        self.assertEqual(procurement_order.state, u'running')
        self.assertEqual(
            procurement_order.purchase_id.payment_mode_id, self.payment_mode)
        self.assertTrue(
            procurement_order.purchase_id.supplier_partner_bank_id.id
            in self.partner.bank_ids.ids)
