# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form, TransactionCase


class TestAccountPaymentOrderNotification(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payment_mode = cls.env.ref("account_payment_mode.payment_mode_inbound_dd1")
        cls.partner_a = cls.env["res.partner"].create({"name": "Test partner A"})
        cls.partner_a_child = cls.env["res.partner"].create(
            {
                "name": "Invoice",
                "type": "invoice",
                "email": "partner-a@test.com",
                "parent_id": cls.partner_a.id,
            }
        )
        cls.partner_b = cls.env["res.partner"].create(
            {"name": "Test partner B", "email": "partner-b@test.com"}
        )
        cls.partner_c = cls.env["res.partner"].create({"name": "Test partner C"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "list_price": 100}
        )
        cls.mt_comment = cls.env.ref("mail.mt_comment")

    def _create_invoice(self, partner, move_type="out_invoice"):
        invoice_form = Form(
            self.env["account.move"].with_context(default_move_type=move_type)
        )
        invoice_form.partner_id = partner
        invoice_form.payment_mode_id = self.payment_mode
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
        return invoice_form.save()

    def _test_notification_from_partner(self, po, partner, total):
        notification = po.notification_ids.filtered(lambda x: x.partner_id == partner)
        self.assertEqual(len(notification.payment_line_ids), total)
        self.assertIn(partner, notification.mapped("message_follower_ids.partner_id"))
        self.assertIn(self.mt_comment, notification.mapped("message_ids.subtype_id"))

    def test_wizard_account_payment_order_notification(self):
        self._create_invoice(self.partner_a_child)
        self._create_invoice(self.partner_a_child)
        self._create_invoice(self.partner_b)
        self._create_invoice(self.partner_c)
        partners = self.partner_a_child + self.partner_b + self.partner_c
        invoices = self.env["account.move"].search([("partner_id", "in", partners.ids)])
        invoices.action_post()
        wizard = (
            self.env["account.invoice.payment.line.multi"]
            .with_context(active_model=invoices._name, active_ids=invoices.ids)
            .create({})
        )
        res = wizard.run()
        payment_order = self.env[res["res_model"]].browse(res["res_id"])
        old_messages = payment_order.message_ids
        template_xml_id = "%s.%s" % (
            "account_payment_order_notification",
            "email_account_payment_order_notification",
        )
        wizard = (
            self.env["wizard.account.payment.order.notification"]
            .with_context(active_id=payment_order.id)
            .create({"mail_template_id": self.env.ref(template_xml_id).id})
        )
        self.assertEqual(len(wizard.line_ids), 3)
        line_a = wizard.line_ids.filtered(
            lambda x: x.partner_id == self.partner_a_child
        )
        self.assertEqual(line_a.email, self.partner_a_child.email)
        self.assertTrue(line_a.to_send)
        line_b = wizard.line_ids.filtered(lambda x: x.partner_id == self.partner_b)
        self.assertEqual(line_b.email, self.partner_b.email)
        self.assertTrue(line_b.to_send)
        line_c = wizard.line_ids.filtered(lambda x: x.partner_id == self.partner_c)
        self.assertFalse(line_c.email)
        self.assertFalse(line_c.to_send)
        wizard.action_process()
        self._test_notification_from_partner(payment_order, self.partner_a_child, 2)
        self._test_notification_from_partner(payment_order, self.partner_b, 1)
        self.assertNotIn(
            self.partner_c, payment_order.mapped("notification_ids.partner_id")
        )
        new_messages = payment_order.message_ids - old_messages
        self.assertIn(self.env.ref("mail.mt_note"), new_messages.mapped("subtype_id"))
