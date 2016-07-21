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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class payment_order_create(orm.TransientModel):
    _inherit = 'payment.order.create'

    def extend_payment_order_domain(
            self, cr, uid, payment_order, domain, context=None):
        if payment_order.payment_order_type == 'payment':
            domain += [
                ('account_id.type', 'in', ('payable', 'receivable')),
                ('amount_to_pay', '>', 0)
            ]
        return True

    def search_entries(self, cr, uid, ids, context=None):
        """
        This method taken from account_payment module.
        We adapt the domain based on the payment_order_type
        """
        line_obj = self.pool.get('account.move.line')
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, ['duedate'], context=context)[0]
        search_due_date = data['duedate']

        # start account_banking_payment
        payment = self.pool.get('payment.order').browse(
            cr, uid, context['active_id'], context=context)
        # Search for move line to pay:
        domain = [
            ('move_id.state', '=', 'posted'),
            ('reconcile_id', '=', False),
            ('company_id', '=', payment.mode.company_id.id),
        ]
        self.extend_payment_order_domain(
            cr, uid, payment, domain, context=context)
        # end account_direct_debit

        domain = domain + [
            '|', ('date_maturity', '<=', search_due_date),
            ('date_maturity', '=', False)
        ]
        line_ids = line_obj.search(cr, uid, domain, context=context)
        context.update({'line_ids': line_ids})
        model_data_ids = mod_obj.search(
            cr, uid, [
                ('model', '=', 'ir.ui.view'),
                ('name', '=', 'view_create_payment_order_lines')],
            context=context)
        resource_id = mod_obj.read(
            cr, uid, model_data_ids, fields=['res_id'],
            context=context)[0]['res_id']
        return {
            'name': _('Entry Lines'),
            'context': context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payment.order.create',
            'views': [(resource_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def _prepare_payment_line(self, cr, uid, payment, line, context=None):
        '''This function is designed to be inherited
        The resulting dict is passed to the create method of payment.line'''
        _today = fields.date.context_today(self, cr, uid, context=context)
        if payment.date_prefered == "now":
            # no payment date => immediate payment
            date_to_pay = False
        elif payment.date_prefered == 'due':
            # account_banking
            # date_to_pay = line.date_maturity
            date_to_pay = (
                line.date_maturity
                if line.date_maturity and line.date_maturity > _today
                else False)
            # end account banking
        elif payment.date_prefered == 'fixed':
            # account_banking
            # date_to_pay = payment.date_scheduled
            date_to_pay = (
                payment.date_scheduled
                if payment.date_scheduled and payment.date_scheduled > _today
                else False)
            # end account banking

        # account_banking
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
        # end account_banking

        # account banking
        # t = None
        # line2bank = line_obj.line2bank(cr, uid, line_ids, t, context)
        line2bank = self.pool['account.move.line'].line2bank(
            cr, uid, [line.id], payment.mode.id, context)
        # end account banking

        res = {
            'move_line_id': line.id,
            'amount_currency': amount_currency,
            'bank_id': line2bank.get(line.id),
            'order_id': payment.id,
            'partner_id': line.partner_id and line.partner_id.id or False,
            # account banking
            # 'communication': line.ref or '/'
            'communication': communication,
            'state': state,
            # end account banking
            'date': date_to_pay,
            'currency': (line.invoice and line.invoice.currency_id.id or
                         line.journal_id.currency.id or
                         line.journal_id.company_id.currency_id.id),
        }
        return res

    def create_payment(self, cr, uid, ids, context=None):
        '''
        This method is a slightly modified version of the existing method on
        this model in account_payment.
        - pass the payment mode to line2bank()
        - allow invoices to create influence on the payment process: not only
        'Free' references are allowed, but others as well
        - check date_to_pay is not in the past.
        '''
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        line_ids = data['entries']
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}

        payment = self.pool['payment.order'].browse(
            cr, uid, context['active_id'], context=context)
        # Populate the current payment with new lines:
        for line in self.pool['account.move.line'].browse(
                cr, uid, line_ids, context=context):
            vals = self._prepare_payment_line(
                cr, uid, payment, line, context=context)
            self.pool['payment.line'].create(cr, uid, vals, context=context)
        # Force reload of payment order view as a workaround for lp:1155525
        return {
            'name': _('Payment Orders'),
            'context': context,
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'payment.order',
            'res_id': context['active_id'],
            'type': 'ir.actions.act_window',
        }
