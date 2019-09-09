# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonTestCase


class TestSaleOrder(CommonTestCase):
    def create_sale_order(self, payment_mode=None):
        so_lines = [
            (
                0,
                0,
                {
                    "name": p.name,
                    "product_id": p.id,
                    "product_uom_qty": 2,
                    "product_uom": p.uom_id.id,
                    "price_unit": p.list_price,
                },
            )
            for (_, p) in self.products.items()
        ]
        so = self.env["sale.order"].create(
            {
                "partner_id": self.base_partner.id,
                "partner_invoice_id": self.base_partner.id,
                "partner_shipping_id": self.base_partner.id,
                "order_line": so_lines,
                "pricelist_id": self.env.ref("product.list0").id,
            }
        )
        self.assertFalse(so.payment_mode_id)
        so.onchange_partner_id()
        self.assertEqual(
            so.payment_mode_id, self.base_partner.customer_payment_mode_id
        )
        # force payment mode
        if payment_mode:
            so.payment_mode_id = payment_mode.id
        return so

    def create_invoice_and_check(
        self, order, expected_payment_mode, expected_partner_bank
    ):
        order.action_confirm()
        order.action_invoice_create()
        invoice = order.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.payment_mode_id, expected_payment_mode)
        self.assertEqual(invoice.partner_bank_id, expected_partner_bank)

    def test_sale_to_invoice_payment_mode(self):
        """
        Data:
            A partner with a specific payment_mode
            A sale order created with the payment_mode of the partner
        Test case:
            Create the invoice from the sale order
        Expected result:
            The invoice must be created with the payment_mode of the partner
        """
        order = self.create_sale_order()
        self.create_invoice_and_check(order, self.payment_mode, self.bank)

    def test_sale_to_invoice_payment_mode_2(self):
        """
        Data:
            A partner with a specific payment_mode
            A sale order created with an other payment_mode
        Test case:
            Create the invoice from the sale order
        Expected result:
            The invoice must be created with the specific payment_mode
        """
        order = self.create_sale_order(payment_mode=self.payment_mode_2)
        self.create_invoice_and_check(order, self.payment_mode_2, self.bank)

    def test_sale_to_invoice_payment_mode_via_payment(self):
        """
        Data:
            A partner with a specific payment_mode
            A sale order created with an other payment_mode
        Test case:
            Create the invoice from sale.advance.payment.inv
        Expected result:
            The invoice must be created with the specific payment_mode
        """
        order = self.create_sale_order(payment_mode=self.payment_mode_2)
        context = {
            "active_model": "sale.order",
            "active_ids": [order.id],
            "active_id": order.id,
        }
        order.action_confirm()
        payment = self.env["sale.advance.payment.inv"].create(
            {
                "advance_payment_method": "fixed",
                "amount": 5,
                "product_id": self.env.ref("sale.advance_product_0").id,
            }
        )
        payment.with_context(context).create_invoices()
        invoice = order.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.payment_mode_id, self.payment_mode_2)
        self.assertEqual(invoice.partner_bank_id, self.bank)
