# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountPaymentOrderNotification(models.Model):
    _name = "account.payment.order.notification"
    _description = "Payment Order Notification"
    _inherit = ["mail.thread"]

    order_id = fields.Many2one(
        comodel_name="account.payment.order",
        required=True,
        readonly=True,
    )
    company_id = fields.Many2one(related="order_id.company_id")
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        required=True,
        readonly=True,
    )
    payment_line_ids = fields.Many2many(
        comodel_name="account.payment.line", readonly=True
    )
    display_name = fields.Char(compute="_compute_display_name")

    @api.depends("order_id", "partner_id")
    def _compute_display_name(self):
        for item in self:
            item.display_name = "[{}] {}".format(
                item.order_id.name, item.partner_id.display_name
            )

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        mt_comment = self.env.ref("mail.mt_comment")
        for rec in res:
            for follower in rec.order_id.message_follower_ids:
                rec.message_subscribe(
                    partner_ids=[follower.partner_id.id],
                    subtype_ids=follower.subtype_ids.ids,
                )
            rec.message_subscribe(
                partner_ids=[rec.partner_id.id],
                subtype_ids=mt_comment.ids,
            )
        return res
