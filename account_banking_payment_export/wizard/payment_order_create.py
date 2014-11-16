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

from openerp import models, fields, api, _


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'

    populate_results = fields.Boolean(string="Populate results directly",
                                      default=True)

    @api.model
    def default_get(self, field_list):
        res = super(PaymentOrderCreate, self).default_get(field_list)
        context = self.env.context
        if ('entries' in field_list and context.get('line_ids') and
                context.get('populate_results')):
            res.update({'entries': context['line_ids']})
        return res

    @api.model
    def extend_payment_order_domain(self, payment_order, domain):
        if payment_order.payment_order_type == 'payment':
            domain += [('account_id.type', 'in', ('payable', 'receivable')),
                       ('amount_to_pay', '>', 0)]
        return True

    @api.multi
    def search_entries(self):
        """This method taken from account_payment module.
        We adapt the domain based on the payment_order_type
        """
        line_obj = self.env['account.move.line']
        model_data_obj = self.env['ir.model.data']
        # -- start account_banking_payment --
        payment = self.env['payment.order'].browse(
            self.env.context['active_id'])
        # Search for move line to pay:
        domain = [('move_id.state', '=', 'posted'),
                  ('reconcile_id', '=', False),
                  ('company_id', '=', payment.mode.company_id.id)]
        self.extend_payment_order_domain(payment, domain)
        # -- end account_direct_debit --
        domain += ['|',
                   ('date_maturity', '<=', self.duedate),
                   ('date_maturity', '=', False)]
        lines = line_obj.search(domain)
        context = self.env.context.copy()
        context['line_ids'] = lines.ids
        context['populate_results'] = self.populate_results
        model_datas = model_data_obj.search(
            [('model', '=', 'ir.ui.view'),
             ('name', '=', 'view_create_payment_order_lines')])
        return {'name': _('Entry Lines'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'payment.order.create',
                'views': [(model_datas[0].res_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                }

    @api.model
    def _prepare_payment_line(self, payment, line):
        """This function is designed to be inherited
        The resulting dict is passed to the create method of payment.line"""
        _today = fields.Date.context_today(self)
        date_to_pay = False  # no payment date => immediate payment
        if payment.date_prefered == 'due':
            # -- account_banking
            # date_to_pay = line.date_maturity
            date_to_pay = (
                line.date_maturity
                if line.date_maturity and line.date_maturity > _today
                else False)
            # -- end account banking
        elif payment.date_prefered == 'fixed':
            # -- account_banking
            # date_to_pay = payment.date_scheduled
            date_to_pay = (
                payment.date_scheduled
                if payment.date_scheduled and payment.date_scheduled > _today
                else False)
            # -- end account banking
        # -- account_banking
        state = 'normal'
        communication = line.ref or '-'
        if line.invoice:
            if line.invoice.type in ('in_invoice', 'in_refund'):
                if line.invoice.reference_type == 'structured':
                    state = 'structured'
                    communication = line.invoice.reference
                else:
                    if line.invoice.reference:
                        communication = line.invoice.reference
                    elif line.invoice.supplier_invoice_number:
                        communication = line.invoice.supplier_invoice_number
            else:
                # Make sure that the communication includes the
                # customer invoice number (in the case of debit order)
                communication = line.invoice.number.replace('/', '')
                state = 'structured'
        # support debit orders when enabled
        if (payment.payment_order_type == 'debit' and
                'amount_to_receive' in line):
            amount_currency = line.amount_to_receive
        else:
            amount_currency = line.amount_to_pay
        line2bank = line.line2bank(payment.mode.id)
        # -- end account banking
        res = {'move_line_id': line.id,
               'amount_currency': amount_currency,
               'bank_id': line2bank.get(line.id),
               'order_id': payment.id,
               'partner_id': line.partner_id and line.partner_id.id or False,
               # account banking
               'communication': communication,
               'state': state,
               # end account banking
               'date': date_to_pay,
               'currency': (line.invoice and line.invoice.currency_id.id
                            or line.journal_id.currency.id
                            or line.journal_id.company_id.currency_id.id)}
        return res

    @api.multi
    def create_payment(self):
        """This method is a slightly modified version of the existing method on
        this model in account_payment.
        - pass the payment mode to line2bank()
        - allow invoices to create influence on the payment process: not only
          'Free' references are allowed, but others as well
        - check date_to_pay is not in the past.
        """
        if not self.entries:
            return {'type': 'ir.actions.act_window_close'}
        context = self.env.context
        payment_line_obj = self.env['payment.line']
        payment = self.env['payment.order'].browse(context['active_id'])
        # Populate the current payment with new lines:
        for line in self.entries:
            vals = self._prepare_payment_line(payment, line)
            payment_line_obj.create(vals)
        # Force reload of payment order view as a workaround for lp:1155525
        return {'name': _('Payment Orders'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'payment.order',
                'res_id': context['active_id'],
                'type': 'ir.actions.act_window'}
