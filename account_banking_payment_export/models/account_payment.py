# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions, workflow, _


class PaymentOrder(models.Model):
    _inherit = 'payment.order'

    payment_order_type = fields.Selection(
        [('payment', 'Payment'), ('debit', 'Direct debit')],
        'Payment order type', required=True, default='payment',
        readonly=True, states={'draft': [('readonly', False)]})
    mode_type = fields.Many2one('payment.mode.type', related='mode.type',
                                string='Payment Type')
    total = fields.Float(compute='_compute_total', store=True)

    @api.depends('line_ids', 'line_ids.amount')
    @api.one
    def _compute_total(self):
        self.total = sum(self.mapped('line_ids.amount') or [0.0])

    @api.multi
    def launch_wizard(self):
        """Search for a wizard to launch according to the type.
        If type is manual. just confirm the order.
        Previously (pre-v6) in account_payment/wizard/wizard_pay.py
        """
        context = self.env.context.copy()
        order = self[0]
        # check if a wizard is defined for the first order
        if order.mode.type and order.mode.type.ir_model_id:
            context['active_ids'] = self.ids
            wizard_model = order.mode.type.ir_model_id.model
            wizard_obj = self.env[wizard_model]
            return {
                'name': wizard_obj._description or _('Payment Order Export'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': wizard_model,
                'domain': [],
                'context': context,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'nodestroy': True,
            }
        else:
            # should all be manual orders without type or wizard model
            for order in self[1:]:
                if order.mode.type and order.mode.type.ir_model_id:
                    raise exceptions.Warning(
                        _('Error'),
                        _('You can only combine payment orders of the same '
                          'type'))
            # process manual payments
            for order_id in self.ids:
                workflow.trg_validate(self.env.uid, 'payment.order',
                                      order_id, 'done', self.env.cr)
            return {}

    @api.multi
    def action_done(self):
        self.write({
            'date_done': fields.Date.context_today(self),
            'state': 'done',
            })
        return True
