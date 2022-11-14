# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    notification_ids = fields.One2many(
        comodel_name="account.payment.order.notification",
        inverse_name="order_id",
        string="Notifications",
    )
    notification_count = fields.Integer(
        string="Notification count", compute="_compute_notification_count"
    )

    def _compute_notification_count(self):
        notification_data = self.env["account.payment.order.notification"].read_group(
            [("order_id", "in", self.ids)], ["order_id"], ["order_id"]
        )
        mapped_data = {r["order_id"][0]: r["order_id_count"] for r in notification_data}
        for record in self:
            record.notification_count = mapped_data.get(record.id, 0)

    def action_view_notifications(self):
        self.ensure_one()
        xml_id = "%s.%s" % (
            "account_payment_order_notification",
            "account_payment_order_notification_action",
        )
        action = self.env["ir.actions.act_window"]._for_xml_id(xml_id)
        action["domain"] = [("order_id", "=", self.id)]
        return action

    def _action_send_mail_notifications(self, template):
        for notification in self.notification_ids:
            notification.message_post_with_template(template.id)

    def _action_create_note_from_notifications(self):
        body = _("Email has been sent to the following partners: %s") % (
            ", ".join(self.mapped("notification_ids.partner_id.name"))
        )
        self.message_post(body=body)
