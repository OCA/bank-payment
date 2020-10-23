# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountPaymentCondition(models.Model):

    _name = 'account.payment.condition'
    _description = 'Payment Condition'

    @api.depends('payment_mode_id', 'payment_term_id')
    def _compute_name(self):
        for record in self:
            display_name = ''
            if record.payment_mode_id:
                display_name += '['
                display_name += record.payment_mode_id.name
                display_name += '] '
            if record.payment_term_id:
                display_name += record.payment_term_id.name
            record.name = display_name

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        ondelete='restrict',
        default=lambda self:
            self.env['res.company']._company_default_get('account.payment.condition')
    )
    name = fields.Char(
        string="Name",
        compute='_compute_name',
        store=True,
        index=True
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        index=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        index=True,
    )
    payment_mode_id = fields.Many2one(
        comodel_name='account.payment.mode',
        string='Payment Mode',
        required=True,
        index=True,
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Payment Term',
        required=True,
        index=True,
    )
