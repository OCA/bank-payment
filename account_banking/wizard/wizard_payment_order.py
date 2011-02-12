# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) EduSense BV (<http://www.edusense.nl>).
#    All Rights Reserved.
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import datetime
import wizard
import pooler
from tools.misc import UpdateableStr
from tools.translate import _
from account_banking.struct import struct
from account_banking.parsers.convert import str2date, date2str

__doc__ = '''
This module is a slightly modified version of the identical named payment
order wizard in account_payment. The rationale for this bulk copy is the
inability to inherit wizards in OpenERP versions prior to version 6.
The modifications in this wizard allows invoices to create influence on the
payment process: not only 'Free' references are allowed, but others as well.

In order to allow further projects based on account_banking to inherit from
this wizard, the complete wizard is made object oriented, as is should have
been from the start.
'''

today = datetime.date.today

class wizard_payment_order(wizard.interface):
    '''
    Create a payment object with lines corresponding to the account move line
    to pay according to the date and the mode provided by the user.
    Hypothesis:
    - Small number of non-reconcilied move line , payment mode and bank account type,
    - Big number of partner and bank account.

    If a type is given, unsuitable account move lines are ignored.
    '''

    FORM = UpdateableStr()
    FIELDS = {
        'entries': {
            'string':'Entries',
            'type':'many2many',
            'relation': 'account.move.line',
        },
    }
    field_duedate = {
        'duedate': {
            'string': 'Due Date',
            'type': 'date',
            'required': True,
            'default': lambda *a: date2str(today()),
        },
    }
    arch_duedate='''<?xml version="1.0"?>
    <form string="Search Payment lines">
        <field name="duedate" />
    </form>'''


    def search_entries(self, cursor, uid, data, context):
        '''
        Search for invoices that can be paid
        '''
        search_due_date = data['form']['duedate']

        pool = pooler.get_pool(cursor.dbname)
        order_obj = pool.get('payment.order')
        move_line_obj = pool.get('account.move.line')

        payment = order_obj.browse(cursor, uid, data['id'], context=context)
        if payment.mode:
            ctx = '''context="{'journal_id': %d}"''' % payment.mode.journal.id
        else:
            ctx = ''

        # Search account.move.line to pay:
        domain = [
            ('reconcile_id', '=', False),
            ('account_id.type', '=', 'payable'),
            ('amount_to_pay', '>', 0),
            '|', ('date_maturity','<=',search_due_date),
                 ('date_maturity','=',False)
        ]
        line_ids = move_line_obj.search(cursor, uid, domain, context=context)
        self.FORM.string = '''<?xml version="1.0"?>
    <form string="Populate Payment:">
        <field name="entries" colspan="4" height="300" width="800" nolabel="1"
            domain="[('id', 'in', [%s])]" %s
            />
    </form>''' % (','.join([str(x) for x in line_ids]), ctx)
        return {}

    def get_communication(self, line):
        '''
        Method to fill the communication and communication2 lines of a payment
        line. Returns (state, comm1, comm2).
        '''
        if line.invoice.reference_type == 'structured':
            return ('structured', line.invoice.reference, '')
        return ('normal', '', line.invoice.reference)

    def create_payment(self, cursor, uid, data, context):
        '''
        Create payment lines from the data of previously created payable
        invoices
        '''
        ids = data['form']['entries'][0][2]
        if not ids:
            return {}

        pool = pooler.get_pool(cursor.dbname)
        order_obj = pool.get('payment.order')
        move_line_obj = pool.get('account.move.line')
        payment_line_obj = pool.get('payment.line')

        payment = order_obj.browse(cursor, uid, data['id'], context=context)
        ptype = payment.mode and payment.mode.type.id or None
        line2bank = move_line_obj.line2bank(cursor, uid, ids, ptype, context)
        _today = today()
        retval = struct()

        # Populate the current payment with new lines
        for line in move_line_obj.browse(cursor, uid, ids, context=context):
            if payment.date_prefered == 'now':
                # no payment date means immediate payment
                date_to_pay = False
            elif payment.date_prefered == 'due':
                date_to_pay = line.date_maturity and \
                              line.date_maturity > _today and \
                              line.date_maturity or False
            elif payment.date_prefered == 'fixed':
                date_to_pay = payment.date_planned and \
                              payment.date_planned > _today and \
                              payment.date_planned or False
            values = struct(
                move_line_id = line.id,
                amount_currency = line.amount_to_pay,
                bank_id = line2bank.get(line.id),
                order_id = payment.id,
                partner_id = line.partner_id and line.partner_id.id or False,
                date = date_to_pay,
                currency = False,
            )
            if line.invoice:
                values.state, values.communication, values.communication2 = \
                        self.get_communication(line)
                values.currency = line.invoice.currency_id.id,
            payment_line_obj.create(cursor, uid, values, context=context)

        return {}

    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'form',
                'arch': arch_duedate,
                'fields': field_duedate,
                'state': [
                    ('end','_Cancel'),
                    ('search','_Search', '', True)
                ]
            },
         },
        'search': {
            'actions': [search_entries],
            'result': {
                'type': 'form',
                'arch': FORM,
                'fields': FIELDS,
                'state': [
                    ('end','_Cancel'),
                    ('create','_Add to payment order', '', True)
                ]
            },
         },
        'create': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': create_payment,
                'state': 'end'
            }
        },
    }

wizard_payment_order('account_payment.populate_payment')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
