# -*- coding: utf-8 -*-
# (c) 2013-2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields
from openerp.tests import common


class TestAccountPaymentPurchase(common.TransactionCase):
    def setUp(self):
        super(TestAccountPaymentPurchase, self).setUp()
        self.bank = self.env['res.partner.bank'].create(
            {'state': 'bank',
             'bank_name': 'Test bank',
             'acc_number': '1234567890'})
        self.journal = self.env['account.journal'].create(
            {'name': 'Test journal',
             'code': 'TEST',
             'type': 'general'})
        self.payment_mode = self.env['payment.mode'].create(
            {'name': 'Test payment mode',
             'journal': self.journal.id,
             'bank_id': self.bank.id,
             'type': self.env.ref(
                 'account_banking_payment_export.manual_bank_tranfer').id})
        self.partner = self.env['res.partner'].create(
            {'name': 'Test partner',
             'supplier_payment_mode': self.payment_mode.id})
        self.purchase = self.env['purchase.order'].create(
            {'partner_id': self.partner.id,
             'pricelist_id': (
                 self.partner.property_product_pricelist_purchase.id),
             'payment_mode_id': self.payment_mode.id,
             'location_id': self.env['stock.location'].search([], limit=1).id,
             'invoice_method': 'order',
             'order_line': [(0, 0, {'name': 'Test line',
                                    'product_qty': 1.0,
                                    'date_planned': fields.Date.today(),
                                    'price_unit': 1.0})]})

    def test_onchange_partner_id_purchase_order(self):
        res = self.env['purchase.order'].onchange_partner_id(False)
        self.assertEqual(res['value']['payment_mode_id'], False)
        res = self.env['purchase.order'].onchange_partner_id(self.partner.id)
        self.assertEqual(res['value']['payment_mode_id'], self.payment_mode.id)

    def test_purchase_order_invoicing(self):
        self.purchase.signal_workflow('purchase_confirm')
        self.assertEqual(
            self.purchase.invoice_ids[0].payment_mode_id, self.payment_mode)

    def test_picking_from_purchase_order_invoicing(self):
        stockable_product = self.env['product.product'].create(
            {'name': 'Test stockable product',
             'type': 'product'})
        self.purchase.order_line[0].product_id = stockable_product.id
        self.purchase.invoice_method = 'picking'
        self.purchase.signal_workflow('purchase_confirm')
        picking = self.purchase.picking_ids[0]
        invoice_id = picking.action_invoice_create(
            self.journal.id, type='in_invoice')[0]
        invoice = self.env['account.invoice'].browse(invoice_id)
        self.assertEqual(invoice.payment_mode_id, self.payment_mode)

    def test_procurement_buy_payment_mode(self):
        mto_product = self.env['product.product'].create(
            {'name': 'Test buy product',
             'type': 'product',
             'seller_ids': [(0, 0, {'name': self.partner.id})]})
        route = self.env.ref('purchase.route_warehouse0_buy')
        rule = self.env['procurement.rule'].search(
            [('route_id', '=', route.id)], limit=1)
        procurement_order = self.env['procurement.order'].create(
            {'product_id': mto_product.id,
             'rule_id': rule.id,
             'location_id': self.env['stock.location'].search([], limit=1).id,
             'warehouse_id': self.env['stock.warehouse'].search(
                 [], limit=1).id,
             'product_qty': 1,
             'product_uom': mto_product.uom_id.id,
             'name': 'Procurement order test'})
        procurement_order.run()
        self.assertEqual(
            procurement_order.purchase_id.payment_mode_id, self.payment_mode)
