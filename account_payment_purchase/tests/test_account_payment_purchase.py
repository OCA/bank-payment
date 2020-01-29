# Copyright 2013-2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields
from odoo.tests import Form, SavepointCase


class TestAccountPaymentPurchase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountPaymentPurchase, cls).setUpClass()
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test journal", "code": "TEST", "type": "general"}
        )
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test payment mode",
                "fixed_journal_id": cls.journal.id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test partner", "supplier_payment_mode_id": cls.payment_mode.id}
        )
        cls.bank = cls.env["res.partner.bank"].create(
            {
                "bank_name": "Test bank",
                "acc_number": "1234567890",
                "partner_id": cls.partner.id,
            }
        )
        cls.bank2 = cls.env["res.partner.bank"].create(
            {
                "bank_name": "Test bank #2",
                "acc_number": "0123456789",
                "partner_id": cls.partner.id,
            }
        )
        cls.uom_id = cls.env.ref("uom.product_uom_unit").id
        cls.mto_product = cls.env["product.product"].create(
            {
                "name": "Test buy product",
                "type": "product",
                "uom_id": cls.uom_id,
                "uom_po_id": cls.uom_id,
                "seller_ids": [(0, 0, {"name": cls.partner.id})],
            }
        )
        cls.purchase = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "payment_mode_id": cls.payment_mode.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "product_qty": 1.0,
                            "product_id": cls.mto_product.id,
                            "product_uom": cls.uom_id,
                            "date_planned": fields.Datetime.today(),
                            "price_unit": 1.0,
                        },
                    )
                ],
            }
        )

    def test_onchange_partner_id_purchase_order(self):
        self.purchase.onchange_partner_id()
        self.assertEqual(self.purchase.payment_mode_id, self.payment_mode)

    def test_purchase_order_invoicing(self):
        self.purchase.button_confirm()
        picking = self.purchase.picking_ids[0]
        picking.action_confirm()
        picking.move_lines.write({"quantity_done": 1.0})
        picking.button_validate()

        invoice = self.env["account.move"].create(
            {"partner_id": self.partner.id, "type": "in_invoice"}
        )
        with Form(invoice) as inv:
            inv.purchase_id = self.purchase
        self.assertEqual(
            self.purchase.invoice_ids[0].payment_mode_id, self.payment_mode
        )

    def test_picking_from_purchase_order_invoicing(self):
        # Test payment mode
        stockable_product = self.env["product.product"].create(
            {"name": "Test stockable product", "type": "product"}
        )
        self.purchase.order_line[0].product_id = stockable_product
        self.purchase.button_confirm()
        picking = self.purchase.picking_ids[0]
        picking.action_confirm()
        picking.move_lines.write({"quantity_done": 1.0})
        picking.button_validate()

        invoice = self.env["account.move"].create(
            {"partner_id": self.partner.id, "type": "in_invoice"}
        )
        invoice.purchase_id = self.purchase
        invoice._onchange_purchase_auto_complete()
        self.assertEqual(invoice.payment_mode_id, self.payment_mode)
        purchase2 = self.purchase.copy()
        payment_mode2 = self.payment_mode.copy()
        purchase2.payment_mode_id = payment_mode2
        purchase2.button_confirm()
        picking = purchase2.picking_ids[0]
        picking.action_confirm()
        picking.move_lines.write({"quantity_done": 1.0})
        picking.button_validate()
        invoice.purchase_id = purchase2
        result = invoice._onchange_purchase_auto_complete()
        self.assertEqual(
            result and result.get("warning", {}).get("title", False), "Warning"
        )

    def test_picking_from_purchase_order_invoicing_bank(self):
        # Test partner_bank
        stockable_product = self.env["product.product"].create(
            {"name": "Test stockable product", "type": "product"}
        )
        self.purchase.order_line[0].product_id = stockable_product
        self.purchase.payment_mode_id = False
        self.purchase.supplier_partner_bank_id = self.bank
        self.purchase.button_confirm()
        picking = self.purchase.picking_ids[0]
        picking.action_confirm()
        picking.move_lines.write({"quantity_done": 1.0})
        picking.button_validate()

        invoice = self.env["account.move"].create(
            {"partner_id": self.partner.id, "type": "in_invoice"}
        )
        invoice.purchase_id = self.purchase
        invoice._onchange_purchase_auto_complete()
        self.assertEqual(invoice.invoice_partner_bank_id, self.bank)
        purchase2 = self.purchase.copy()
        purchase2.supplier_partner_bank_id = self.bank2
        purchase2.button_confirm()
        picking = purchase2.picking_ids[0]
        picking.action_confirm()
        picking.move_lines.write({"quantity_done": 1.0})
        picking.button_validate()
        invoice.purchase_id = purchase2
        result = invoice._onchange_purchase_auto_complete()
        self.assertEqual(
            result and result.get("warning", {}).get("title", False), "Warning"
        )

    def test_procurement_buy_payment_mode(self):
        route = self.env.ref("purchase_stock.route_warehouse0_buy")
        rule = self.env["stock.rule"].search([("route_id", "=", route.id)], limit=1)
        rule._run_buy(
            procurements=[
                (
                    self.env["procurement.group"].Procurement(
                        self.mto_product,
                        1,
                        self.mto_product.uom_id,
                        self.env["stock.location"].search([], limit=1),
                        "Procurement order test",
                        "Test",
                        rule.company_id,
                        {
                            "company_id": rule.company_id,
                            "date_planned": fields.Datetime.now(),
                        },
                    ),
                    rule,
                )
            ]
        )
        purchase = self.env["purchase.order"].search([("origin", "=", "Test")])
        self.assertEqual(purchase.payment_mode_id, self.payment_mode)
