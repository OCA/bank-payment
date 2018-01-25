# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonTestCase


class TestSaleOrder(CommonTestCase):

    def create_sale_order(self):
        so_lines = [(0, 0, {
            'name': p.name,
            'product_id': p.id,
            'product_uom_qty': 2,
            'product_uom': p.uom_id.id,
            'price_unit': p.list_price,
        }) for (_, p) in self.products.items()]
        so = self.env['sale.order'].create({
            'partner_id': self.base_partner.id,
            'partner_invoice_id': self.base_partner.id,
            'partner_shipping_id': self.base_partner.id,
            'order_line': so_lines,
            'pricelist_id': self.env.ref('product.list0').id,
        })
        self.assertFalse(so.payment_mode_id)
        so.onchange_partner_id()
        self.assertEqual(
            so.payment_mode_id,
            self.base_partner.customer_payment_mode_id
        )
        return so

    def test_sale_to_invoice_payment_mode(self):
        order = self.create_sale_order()
        context = {
            "active_model": 'sale.order',
            "active_ids": [order.id],
            "active_id": order.id,
        }
        order.with_context(context).action_confirm()
        payment = self.env['sale.advance.payment.inv'].create({
            'advance_payment_method': 'fixed',
            'amount': 5,
            'product_id': self.env.ref('sale.advance_product_0').id,
        })
        vals = order._get_payment_mode_vals({})
        expected_vals = {
            'payment_mode_id': self.payment_mode.id,
            'partner_bank_id': self.bank.id,
        }
        self.assertEqual(vals, expected_vals)
        payment.with_context(context).create_invoices()
        invoice = order.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(
            invoice.payment_mode_id.id,
            expected_vals["payment_mode_id"]
        )
        self.assertEqual(
            invoice.partner_bank_id.id,
            expected_vals["partner_bank_id"]
        )
