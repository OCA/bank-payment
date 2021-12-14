# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    inbound_payment_order_only = fields.Boolean(
        compute="_compute_inbound_payment_order_only", readonly=True, store=True
    )
    outbound_payment_order_only = fields.Boolean(
        compute="_compute_outbound_payment_order_only", readonly=True, store=True
    )

    @api.depends("inbound_payment_method_line_ids.payment_method_id.payment_order_only")
    def _compute_inbound_payment_order_only(self):
        for rec in self:
            rec.inbound_payment_order_only = all(
                p.payment_order_only
                for p in rec.inbound_payment_method_line_ids.payment_method_id
            )

    @api.depends(
        "outbound_payment_method_line_ids.payment_method_id.payment_order_only"
    )
    def _compute_outbound_payment_order_only(self):
        for rec in self:
            rec.outbound_payment_order_only = all(
                p.payment_order_only
                for p in rec.outbound_payment_method_line_ids.payment_method_id
            )
