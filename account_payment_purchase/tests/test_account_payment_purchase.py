# Copyright 2013-2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import Command
from odoo.tests import Form, TransactionCase, tagged
from odoo.tools import mute_logger


@tagged("-at_install", "post_install")
class TestAccountPaymentPurchase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test journal", "code": "TEST", "type": "general"}
        )
        cls.payment_method_out = cls.env.ref(
            "account.account_payment_method_manual_out"
        )
        cls.payment_method_out.bank_account_required = True
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test payment mode",
                "fixed_journal_id": cls.journal.id,
                "bank_account_link": "variable",
                "payment_method_id": cls.payment_method_out.id,
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
                "uom_id": cls.uom_id,
                "uom_po_id": cls.uom_id,
                "seller_ids": [Command.create({"partner_id": cls.partner.id})],
            }
        )
        order_form = Form(cls.env["purchase.order"])
        order_form.partner_id = cls.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.mto_product
            line_form.product_qty = 1
        cls.purchase = order_form.save()

    def test_onchange_partner_id_purchase_order(self):
        self.assertEqual(self.purchase.payment_mode_id, self.payment_mode)

    @mute_logger("odoo.models.unlink")
    def test_purchase_order_create_invoice(self):
        self.purchase.button_confirm()
        self.purchase.order_line.qty_received = 1
        res = self.purchase.action_create_invoice()
        invoice = self.env[res["res_model"]].browse(res["res_id"])
        self.assertEqual(invoice.partner_bank_id, self.bank)
        # Remove the invoice and try another use case
        invoice.unlink()
        self.payment_method_out.bank_account_required = False
        res = self.purchase.action_create_invoice()
        invoice2 = self.env[res["res_model"]].browse(res["res_id"])
        self.assertFalse(invoice2.partner_bank_id)

    def test_purchase_order_invoicing(self):
        self.purchase.button_confirm()
        invoice = self.env["account.move"].create(
            {"partner_id": self.partner.id, "move_type": "in_invoice"}
        )
        invoice.purchase_id = self.purchase
        invoice._onchange_purchase_auto_complete()
        self.assertEqual(
            self.purchase.invoice_ids[0].payment_mode_id, self.payment_mode
        )

    def test_from_purchase_order_invoicing(self):
        # Test payment mode
        product = self.env["product.product"].create({"name": "Test product"})
        self.purchase.order_line[0].product_id = product
        self.purchase.button_confirm()

        invoice = self.env["account.move"].create(
            {"partner_id": self.partner.id, "move_type": "in_invoice"}
        )
        invoice.purchase_id = self.purchase
        invoice._onchange_purchase_auto_complete()
        self.assertEqual(invoice.payment_mode_id, self.payment_mode)
        purchase2 = self.purchase.copy()
        payment_mode2 = self.payment_mode.copy()
        purchase2.payment_mode_id = payment_mode2
        purchase2.button_confirm()

        invoice.purchase_id = purchase2
        result = invoice._onchange_purchase_auto_complete()
        self.assertEqual(
            result and result.get("warning", {}).get("title", False), "Warning"
        )

    def test_from_purchase_order_invoicing_bank(self):
        # Test partner_bank
        product = self.env["product.product"].create({"name": "Test product"})
        self.purchase.order_line[0].product_id = product
        self.purchase.supplier_partner_bank_id = self.bank
        self.purchase.button_confirm()
        invoice = self.env["account.move"].create(
            {"partner_id": self.partner.id, "move_type": "in_invoice"}
        )
        invoice.purchase_id = self.purchase
        invoice._onchange_purchase_auto_complete()
        self.assertEqual(invoice.partner_bank_id, self.bank)
        purchase2 = self.purchase.copy()
        purchase2.supplier_partner_bank_id = self.bank2
        purchase2.button_confirm()

        invoice.purchase_id = purchase2
        result = invoice._onchange_purchase_auto_complete()
        self.assertEqual(
            result and result.get("warning", {}).get("title", False), "Warning"
        )
