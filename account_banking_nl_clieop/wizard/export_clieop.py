# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#    All Rights Reserved
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

import wizard
import pooler
import base64
from datetime import datetime, date, timedelta
from account_banking import sepa
#from osv import osv
from tools.translate import _
#import pdb; pdb.set_trace()
import clieop

form = '''<?xml version="1.0"?>
<form string="Client Opdrachten Export">
    <separator colspan="4" string="Processing Details" />
    <field name="batchtype" />
    <field name="execution_date" />
    <field name="test" />
    <separator colspan="4" string="Reference for further communication" />
    <field name="reference" colspan="2" />
    <separator colspan="4" string="Additional message for all transactions" />
    <field name="fixed_message" />
</form>'''

fields = {
    'reference' : {
        'string': 'Reference',
        'type': 'char',
        'size': 5,
        'required': False,
        'help': ('The bank will use this reference in feedback communication '
                 'to refer to this run. Only five characters are available.'
                )
    },
    'batchtype': {
        'string': 'Type',
        'type': 'selection',
        'selection': [
            ('CLIEOPPAY', 'Payments'),
            ('CLIEOPSAL', 'Salary Payments'),
            ('CLIEOPINC', 'Direct Debits'),
        ],
        'readonly': True,
    },
    'execution_date': {
        'string': 'Execution Date',
        'type': 'date',
        'required': False,
        'help': ('This is the date the file should be processed by the bank. '
                 'Don\'t choose a date beyond the nearest date in your '
                 'payments. The latest allowed date is 30 days from now.\n'
                 'Please keep in mind that banks only execute on working days '
                 'and typically use a delay of two days between execution date '
                 'and effective transfer date.'
                ),
    },
    'test': {
        'string': 'Test Run',
        'type': 'boolean',
        'required': True,
        'default': True,
        'help': ('Select this if you want your bank to run a test process '
                 'rather then execute your orders for real.'
                )
    },
    'fixed_message': {
        'string': 'Fixed Message',
        'type': 'char',
        'size': 32,
        'required': False,
        'default': '',
        'help': ('A fixed message to apply to all transactions in addition to '
                 'the individual messages.'
                ),
    },
}

file_form = '''<?xml version="1.0"?>
<form string="Client Opdrachten Export">
    <field name="filetype" />
    <field name="identification" />
    <field name="total_amount" />
    <field name="check_no_accounts" />
    <field name="no_transactions" />
    <field name="prefered_date" />
    <field name="testcode" />
    <newline/>
    <field name="file" />
    <field name="log" colspan="4" nolabel="1" />
</form>'''

file_fields = {
    'testcode': {
        'string': 'Test Run',
        'type': 'selection',
        'selection': [('T', _('Yes')), ('P', _('No'))],
        'required': False,
        'readonly': True,
    },
    'prefered_date': {
        'string': 'Prefered Processing Date',
        'type': 'date',
        'required': False,
        'readonly': True,
    },
    'no_transactions': {
        'string': 'Number of Transactions',
        'type': 'int',
        'required': False,
        'readonly': True,
    },
    'check_no_accounts': {
        'string': 'Check Number Accounts',
        'type': 'char',
        'size': 5,
        'required': False,
        'readonly': True,
    },
    'total_amount': {
        'string': 'Total Amount',
        'type': 'float',
        'required': False,
        'readonly': True,
    },
    'identification': {
        'string': 'Identification',
        'type': 'char',
        'size': 6,
        'required': False,
        'readonly': True,
    },
    'filetype': {
        'string': 'File Type',
        'type': 'selection',
        'selection': [
            ('CREDBET', 'Payment Batch'),
            ('SALARIS', 'Salary Payment Batch'),
            ('INCASSO', 'Direct Debit Batch'),
        ],
        'required': False,
        'readonly': True,
    },
    'file': {
        'string': 'ClieOp File',
        'type': 'binary',
        'required': False,
        'readonly': True,
    },
    'log': {
        'string': 'Log',
        'type': 'text',
        'readonly': True,
    },
}

def strpdate(arg, format='%Y-%m-%d'):
    '''shortcut'''
    return datetime.strptime(arg, format).date()

def strfdate(arg, format='%Y-%m-%d'):
    '''shortcut'''
    return arg.strftime(format)

def _check_orders(self, cursor, uid, data, context):
    '''
    Check payment type for all orders.

    Combine orders into one. All parameters harvested by the wizard
    will apply to all orders. This will in effect create one super
    batch for ClieOp, instead of creating individual parameterized
    batches. As only large companies are likely to need the individual
    settings per batch, this will do for now.
    '''
    form = data['form']
    today = date.today()
    pool = pooler.get_pool(cursor.dbname)
    payment_order_obj = pool.get('payment.order')

    runs = {}
    # Only orders of same type can be combined
    payment_orders = payment_order_obj.browse(cursor, uid, data['ids'])
    for payment_order in payment_orders:

        payment_type = payment_order.mode.type.code
        if payment_type in runs:
            runs[payment_type].append(payment_order)
        else:
            runs[payment_type] = [payment_order]

        if payment_order.date_prefered == 'fixed':
            if payment_order.date_planned:
                execution_date = strpdate(payment_order.date_planned)
            else:
                execution_date = today
        elif payment_order.date_prefered == 'now':
            execution_date = today
        elif payment_order.date_prefered == 'due':
            # Max processing date is 30 days past now, so limiting beyond that
            # will catch too early payments
            max_date = execution_date = today + timedelta(days=31)
            for line in payment_order.line_ids:
                if line.move_line_id.date_maturity:
                    date_maturity = strpdate(line.move_line_id.date_maturity)
                    if date_maturity < execution_date:
                        execution_date = date_maturity
                else:
                    execution_date = today
            if execution_date and execution_date >= max_date:
                raise wizard.except_wizard(
                    _('Error'),
                    _('You can\'t create ClieOp orders more than 30 days in advance.')
                )
        # Sanity check: can't process in the past
        form['execution_date'] = strfdate(max(execution_date, today))

    if len(runs) != 1:
        raise wizard.except_wizard(
            _('Error'),
            _('You can only combine payment orders of the same type')
        )

    form['batchtype'] = type = runs.keys()[0]
    form['reference'] = runs[type][0].reference[-5:]
    return form

def _create_clieop(self, cursor, uid, data, context):
    '''
    Wizard to actually create the ClieOp3 file
    '''
    pool = pooler.get_pool(cursor.dbname)
    payment_order_obj = pool.get('payment.order')
    form = data['form']

    clieopfile = None
    payment_orders = payment_order_obj.browse(cursor, uid, data['ids'])
    for payment_order in payment_orders:
        if not clieopfile:
            # Just once: create clieop file
            our_account_owner = payment_order.mode.bank_id.owner_name
            our_account_nr = payment_order.mode.bank_id.acc_number
            if not our_account_nr and payment_order.mode.bank_id.iban:
                our_account_nr = sepa.IBAN(
                    payment_order.mode.bank_id.iban
                ).localized_BBAN
                if not our_account_nr:
                    raise wizard.except_wizard(
                        _('Error'),
                        _('Your bank account has to have a valid account number')
                    )
            clieopfile = {'CLIEOPPAY': clieop.PaymentsFile,
                          'CLIEOPINC': clieop.DirectDebitFile,
                          'CLIEOPSAL': clieop.SalaryPaymentsFile,
                         }[form['batchtype']](
                             identification = form['reference'],
                             execution_date = form['execution_date'],
                             name_sender = our_account_owner,
                             accountno_sender = our_account_nr,
                             test = form['test']
                         )

        # As payment_orders can have multiple transactions, create a new batch
        # for each payment_order
        if form['fixed_message']:
            messages = [form['fixed_message']]
        else:
            messages = []
        batch = clieopfile.batch(
            messages = messages,
            batch_id = payment_order.reference
        )

        for line in payment_order.line_ids:
            kwargs = dict(
                name = line.bank_id.owner_name,
                amount = line.amount_currency,
                reference = line.communication or None,
            )
            if line.communication2:
                kwargs['messages'] = [line.communication2]
            other_account_nr = line.bank_id.acc_number
            iban = sepa.IBAN(other_account_nr)
            if iban.valid:
                if iban.countrycode != 'NL':
                    raise wizard.except_wizard(
                        _('Error'),
                        _('You cannot send international bank transfers '
                          'through ClieOp3!')
                    )
                other_account_nr = iban.localized_BBAN
            if form['batchtype'] == 'CLIEOPINC':
                kwargs['accountno_beneficiary'] = our_account_nr
                kwargs['accountno_payer'] = other_account_nr
            else:
                kwargs['accountno_beneficiary'] = other_account_nr
                kwargs['accountno_payer'] = our_account_nr
            transaction = batch.transaction(**kwargs)

    # Generate the specifics of this clieopfile
    order = clieopfile.order
    values = dict(
        filetype = order.name_transactioncode,
        identification = order.identification,
        prefered_date = strfdate(order.preferred_execution_date),
        total_amount = int(order.total_amount) / 100.0,
        check_no_accounts = order.total_accountnos,
        no_transactions = order.nr_posts,
        testcode = order.testcode,
        file = base64.encodestring(clieopfile.rawdata),
    )
    form.update(values)
    values['daynumber'] = int(clieopfile.header.file_id[2:])
    values['payment_order_ids'] = ','.join(map(str, data['ids']))
    data['file_id'] = pool.get('banking.export.clieop').create(cursor, uid, values)
    data['clieop'] = clieopfile
    form['log'] = ''
    return form

def _cancel_clieop(self, cursor, uid, data, context):
    '''
    Cancel the ClieOp: just drop the file
    '''
    pool = pooler.get_pool(cursor.dbname)
    pool.get('banking.export.clieop').unlink(cursor, uid, data['file_id'])
    return {'state': 'end'}

def _save_clieop(self, cursor, uid, data, context):
    '''
    Save the ClieOp: mark all payments in the file as 'sent'.
    '''
    pool = pooler.get_pool(cursor.dbname)
    clieop_obj = pool.get('banking.export.clieop')
    payment_order_obj = pool.get('payment.order')
    clieop_file = clieop_obj.write(
        cursor, uid, data['file_id'], {'state':'sent'}
    )
    payment_order_obj.write(cursor, uid, data['ids'], {'state': 'sent'})
    return {'state': 'end'}

class wizard_banking_export_clieop(wizard.interface):
    states = {
        'init': {
            'actions': [_check_orders],
            'result': {
                'type': 'form',
                'arch': form,
                'fields' : fields,
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('create', 'Create', 'gtk-ok'),
                ]
            }
        },
        'create': {
            'actions': [_create_clieop],
            'result': {
                'type': 'form',
                'arch': file_form,
                'fields': file_fields,
                'state': [
                    ('cancel', 'Cancel', 'gtk-cancel'),
                    ('save', 'Save', 'gtk-save'),
                ]
            },
        },
        'cancel': {
            'actions': [_cancel_clieop],
            'result': {
                'type': 'state',
                'state': 'end'
            }
        },
        'save': {
            'actions': [_save_clieop],
            'result': {
                'type': 'state',
                'state': 'end'
            },
        }
    }
wizard_banking_export_clieop('account_banking_nl_clieop.banking_export_clieop')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
