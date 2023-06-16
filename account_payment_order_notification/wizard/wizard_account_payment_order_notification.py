# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class WizardAccountPaymentOrderNotification(models.TransientModel):
    _name = "wizard.account.payment.order.notification"
    _description = "Wizard Account Payment Order Notification"

    order_id = fields.Many2one(
        comodel_name="account.payment.order",
        required=True,
        readonly=True,
    )
    mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        domain=[("model_id.model", "=", "account.payment.order.notification")],
        required=True,
    )
    line_ids = fields.One2many(
        comodel_name="wizard.account.payment.order.notification.line",
        inverse_name="parent_id",
        string="Lines",
    )

    @api.model
    def default_get(self, fields):
        vals = super().default_get(fields)
        po = self.env["account.payment.order"].browse(
            [self.env.context.get("active_id")]
        )
        if po:
            line_ids = []
            # We need to transfer invoice partner so that the email is sent to the
            # correct partner (not parent)
            for partner in po.payment_line_ids.mapped(
                lambda x: x.move_line_id.move_id.partner_id or x.partner_id
            ):
                line_ids += [
                    (
                        0,
                        0,
                        {
                            "partner_id": partner.id,
                            "email": partner.email,
                            "to_send": True if partner.email else False,
                        },
                    )
                ]
            template_xml_id = "%s.%s" % (
                "account_payment_order_notification",
                "email_account_payment_order_notification",
            )
            vals.update(
                {
                    "order_id": po.id,
                    "line_ids": line_ids,
                    "mail_template_id": self.env.ref(template_xml_id).id,
                }
            )
        return vals

    def action_process(self):
        notifications = []
        for item in self.line_ids.filtered("to_send"):
            payment_line_ids = self.order_id.payment_line_ids.filtered(
                lambda x: x.partner_id == item.partner_id.commercial_partner_id
            )
            data = {
                "partner_id": item.partner_id.id,
                "payment_line_ids": payment_line_ids,
            }
            notifications.append((0, 0, data))
        self.order_id.notification_ids = notifications
        self.order_id._action_send_mail_notifications(self.mail_template_id)
        self.order_id._action_create_note_from_notifications()


class WizardAccountPaymentOrderNotificationLine(models.TransientModel):
    _name = "wizard.account.payment.order.notification.line"
    _description = "Wizard Account Payment Order Notification Line"

    parent_id = fields.Many2one(
        comodel_name="wizard.account.payment.order.notification",
        ondelete="cascade",
        index=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner", required=True, string="Partner", readonly=True
    )
    email = fields.Char()
    to_send = fields.Boolean(string="To send")
