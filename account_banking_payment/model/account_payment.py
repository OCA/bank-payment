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
from openerp import netsvc


class payment_order(orm.Model):
    '''
    Enable extra states for payment exports
    '''
    _inherit = 'payment.order'

    _columns = {
        'date_scheduled': fields.date(
            'Scheduled date if fixed',
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
            help='Select a date if you have chosen Preferred Date to be fixed.'
        ),
        'reference': fields.char(
            'Reference', size=128, required=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'mode': fields.many2one(
            'payment.mode', 'Payment mode', select=True, required=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
            help='Select the Payment Mode to be applied.',
        ),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('open','Confirmed'),
            ('cancel','Cancelled'),
            ('sent', 'Sent'),
            ('rejected', 'Rejected'),
            ('done','Done'),
            ], 'State', select=True
        ),
        'line_ids': fields.one2many(
            'payment.line', 'order_id', 'Payment lines',
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'user_id': fields.many2one(
            'res.users','User', required=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
        ),
        'date_prefered': fields.selection([
            ('now', 'Directly'),
            ('due', 'Due date'),
            ('fixed', 'Fixed date')
            ], "Preferred date", change_default=True, required=True,
            states={
                'sent': [('readonly', True)],
                'rejected': [('readonly', True)],
                'done': [('readonly', True)]
            },
            help=("Choose an option for the Payment Order:'Fixed' stands for a "
                  "date specified by you.'Directly' stands for the direct "
                  "execution.'Due date' stands for the scheduled date of "
                  "execution."
                 )
            ),
        'payment_order_type': fields.selection(
            [('payment', 'Payment'),('debit', 'Direct debit')],
            'Payment order type', required=True,
            ),
        'date_sent': fields.date('Send date', readonly=True),
    }

    _defaults = {
        'payment_order_type': lambda *a: 'payment',
        }

    def launch_wizard(self, cr, uid, ids, context=None):
        """
        Search for a wizard to launch according to the type.
        If type is manual. just confirm the order.
        Previously (pre-v6) in account_payment/wizard/wizard_pay.py
        """
        if context == None:
            context = {}
        result = {}
        orders = self.browse(cr, uid, ids, context)
        order = orders[0]
        # check if a wizard is defined for the first order
        if order.mode.type and order.mode.type.ir_model_id:
            context['active_ids'] = ids
            wizard_model = order.mode.type.ir_model_id.model
            wizard_obj = self.pool.get(wizard_model)
            wizard_id = wizard_obj.create(cr, uid, {}, context)
            result = {
                'name': wizard_obj._description or 'Payment Order Export',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': wizard_model,
                'domain': [],
                'context': context,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': wizard_id,
                'nodestroy': True,
                }
        else:
            # should all be manual orders without type or wizard model
            for order in orders[1:]:
                if order.mode.type and order.mode.type.ir_model_id:
                    raise orm.except_orm(
                        _('Error'),
                        _('You can only combine payment orders of the same type')
                        )
            # process manual payments
            wf_service = netsvc.LocalService('workflow')
            for order_id in ids:
                wf_service.trg_validate(uid, 'payment.order', order_id, 'sent', cr)
        return result

    def _write_payment_lines(self, cr, uid, ids, **kwargs):
        '''
        ORM method for setting attributes of corresponding payment.line objects.
        Note that while this is ORM compliant, it is also very ineffecient due
        to the absence of filters on writes and hence the requirement to
        filter on the client(=OpenERP server) side.
        '''
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        payment_line_obj = self.pool.get('payment.line')
        line_ids = payment_line_obj.search(
            cr, uid, [
                ('order_id', 'in', ids)
            ])
        payment_line_obj.write(cr, uid, line_ids, kwargs)

    def set_to_draft(self, cr, uid, ids, *args):
        '''
        Set both self and payment lines to state 'draft'.
        '''
        self._write_payment_lines(cr, uid, ids, export_state='draft')
        return super(payment_order, self).set_to_draft(
            cr, uid, ids, *args
        )

    def action_sent(self, cr, uid, ids, context=None):
        '''
        Set both self and payment lines to state 'sent'.
        '''
        self._write_payment_lines(cr, uid, ids, export_state='sent')
        self.write(cr, uid, ids, {
                'state':'sent',
                'date_sent': fields.date.context_today(
                    self, cr, uid, context=context),
                }, context=context)
        return True

    def action_rejected(self, cr, uid, ids, *args):
        '''
        Set both self and payment lines to state 'rejected'.
        '''
        self._write_payment_lines(cr, uid, ids, export_state='rejected')
        wf_service = netsvc.LocalService('workflow')
        for id in ids:
            wf_service.trg_validate(uid, 'payment.order', id, 'rejected', cr)
        return True

    def set_done(self, cr, uid, ids, *args):
        '''
        Extend standard transition to update children as well.
        '''
        self._write_payment_lines(
            cr, uid, ids,
            export_state='done',
            date_done=fields.date.context_today(self, cr, uid))
        return super(payment_order, self).set_done(
            cr, uid, ids, *args
        )

    def get_wizard(self, type):
        '''
        Intercept manual bank payments to include 'sent' state. Default
        'manual' payments are flagged 'done' immediately.
        '''
        if type == 'BANKMAN':
            # Note that self._module gets overwritten by inheriters, so make
            # the module name hard coded.
            return 'account_banking', 'wizard_account_banking_payment_manual'
        return super(payment_order, self).get_wizard(type)

    """
    Hooks for processing direct debit orders, such as implemented in
    account_direct_debit module.
    """
    def debit_reconcile_transfer(
        self, cr, uid, payment_order_id, amount, currency, context=None):
        """
        Reconcile the payment order if the amount is correct. Return the 
        id of the reconciliation.
        """
        raise orm.except_orm(
            _("Cannot reconcile"),
            _("Cannot reconcile debit order: "+
              "Not implemented."))

    def debit_unreconcile_transfer(
        self, cr, uid, payment_order_id, reconcile_id, amount, currency,
        context=None):
        """ Unreconcile the payment_order if at all possible """
        raise orm.except_orm(
            _("Cannot unreconcile"),
            _("Cannot unreconcile debit order: "+
              "Not implemented."))
