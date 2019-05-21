# Copyright 2013-2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields
from odoo.addons.account_payment_purchase.tests.\
    test_account_payment_purchase import TestAccountPaymentPurchase


class TestAccountPaymentPurchaseStock(TestAccountPaymentPurchase):

    def test_purchase_stock_order_invoicing(self):
        self.purchase.button_confirm()
        picking = self.purchase.picking_ids[0]
        picking.action_confirm()
        picking.move_lines.write({'quantity_done': 1.0})
        picking.button_validate()

        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'purchase_id': self.purchase.id,
            'account_id': self.partner.property_account_payable_id.id,
        })
        invoice.purchase_order_change()
        self.assertEqual(
            self.purchase.invoice_ids[0].payment_mode_id, self.payment_mode)

    def test_picking_from_purchase_order_invoicing(self):
        # Test payment mode
        stockable_product = self.env['product.product'].create(
            {'name': 'Test stockable product',
             'type': 'product'})
        self.purchase.order_line[0].product_id = stockable_product.id
        self.purchase.button_confirm()
        picking = self.purchase.picking_ids[0]
        picking.action_confirm()
        picking.move_lines.write({'quantity_done': 1.0})
        picking.button_validate()

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
        picking = purchase2.picking_ids[0]
        picking.action_confirm()
        picking.move_lines.write({'quantity_done': 1.0})
        picking.button_validate()
        invoice.purchase_id = purchase2.id
        result = invoice.purchase_order_change()
        self.assertEqual(result['warning']['title'], 'Warning')

    def test_picking_from_purchase_order_invoicing_bank(self):
        # Test patner_bank
        stockable_product = self.env['product.product'].create(
            {'name': 'Test stockable product',
             'type': 'product'})
        self.purchase.order_line[0].product_id = stockable_product.id
        self.purchase.payment_mode_id = False
        self.purchase.supplier_partner_bank_id = self.bank.id
        self.purchase.button_confirm()
        picking = self.purchase.picking_ids[0]
        picking.action_confirm()
        picking.move_lines.write({'quantity_done': 1.0})
        picking.button_validate()

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
        picking = purchase2.picking_ids[0]
        picking.action_confirm()
        picking.move_lines.write({'quantity_done': 1.0})
        picking.button_validate()
        invoice.purchase_id = purchase2.id
        result = invoice.purchase_order_change()
        self.assertEqual(result['warning']['title'], 'Warning')

    def test_stock_rule_buy_payment_mode(self):
        route = self.env.ref('purchase_stock.route_warehouse0_buy')
        rule = self.env['stock.rule'].search(
            [('route_id', '=', route.id)], limit=1)
        rule._run_buy(
            product_id=self.mto_product,
            product_qty=1,
            product_uom=self.mto_product.uom_id,
            location_id=self.env['stock.location'].search([], limit=1),
            name='Procurement order test',
            origin='Test',
            values={
                'company_id': self.env.user.company_id,
                'date_planned': fields.Datetime.now(),
            },
        )
        purchase = self.env['purchase.order'].search([('origin', '=', 'Test')])
        self.assertEqual(purchase.payment_mode_id, self.payment_mode)
