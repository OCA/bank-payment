# Copyright 2020 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountPaymentOrder(models.Model):
    _name = "account.payment.order"
    _inherit = ["account.payment.order", "edi.exchange.consumer.mixin"]

    edi_exchange_type_id = fields.Many2one(
        "edi.exchange.type",
        help="Define which rule it should use to send the file.",
        domain=[("backend_id", "!=", False), ("direction", "=", "output")],
        readonly=True,
        states={"draft": [("readonly", False)], "open": [("readonly", False)]},
    )

    disable_edi_auto = fields.Boolean(
        help="When marked, EDI could be avoided",
        readonly=True,
        states={"draft": [("readonly", False)], "open": [("readonly", False)]},
    )

    def open2generated(self):
        action = super().open2generated()
        if self:
            attachment = self.env["ir.attachment"].browse(action.get("res_id"))
            self.with_context(
                {
                    "exchange_file": attachment.datas,
                    "exchange_filename": attachment.display_name,
                }
            )._event("on_file_generation_payment_order").notify(self)
        return action
