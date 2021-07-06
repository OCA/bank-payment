# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RepairOrder(models.Model):

    _inherit = 'repair.order'

    payment_mode_id = fields.Many2one(
        comodel_name='account.payment.mode',
        string='Payment Mode',
        domain=[('payment_type', '=', 'inbound')]
    )

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        if self.partner_id:
            self.payment_mode_id = self.partner_id.with_context(
                force_company=self.company_id.id
            ).customer_payment_mode_id
        else:
            self.payment_mode_id = False
        return res

    @api.multi
    def action_invoice_create(self, group=False):
        res = super().action_invoice_create(group)
        for record in self:
            if record.invoice_id and record.payment_mode_id:
                record.invoice_id.payment_mode_id = record.payment_mode_id
        return res
