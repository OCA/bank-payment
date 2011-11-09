# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 credativ Ltd (<http://www.credativ.co.uk>).
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
# Import of HSBC data in Swift MT940 format
#

from account_banking.parsers import models
from account_banking.parsers.convert import str2date
from tools.translate import _
from mt940_parser import HSBCParser
import re

bt = models.mem_bank_transaction

def record2float(record, value):
    if record['creditmarker'][-1] == 'C':
        return float(record[value])
    return -float(record[value])

class transaction(models.mem_bank_transaction):

    mapping = {
        'execution_date' : 'valuedate',
        'effective_date' : 'bookingdate',
        'local_currency' : 'currency',
        'transfer_type' : 'bookingcode',
        'reference' : 'custrefno',
        'message' : 'furtherinfo'
    }

    type_map = {
        'TRF': bt.ORDER,
    }

    def __init__(self, record, *args, **kwargs):
        '''
        Transaction creation
        '''
        super(transaction, self).__init__(*args, **kwargs)
        for key, value in self.mapping.iteritems():
            if record.has_key(value):
                setattr(self, key, record[value])

        self.transferred_amount = record2float(record, 'amount')

        #print record.get('bookingcode')
        if not self.is_valid():
            print "Invalid: %s" % record
    def is_valid(self):
        '''
        We don't have remote_account so override base
        '''
        return (self.execution_date
                and self.transferred_amount and True) or False

class statement(models.mem_bank_statement):
    '''
    Bank statement imported data
    '''

    def import_record(self, record):
        def _transmission_number():
            self.id = record['transref']
        def _account_number():
            # The wizard doesn't check for sort code
            self.local_account = record['sortcode'] + ' ' + record['accnum'].zfill(8)
        def _statement_number():
            self.id = '-'.join([self.id, self.local_account, record['statementnr']])
        def _opening_balance():
            self.start_balance = record2float(record,'startingbalance')
            self.currency_code = record['currencycode']
        def _closing_balance():
            self.end_balance = record2float(record, 'endingbalance')
            self.date = record['bookingdate']
        def _transaction_new():
            self.transactions.append(transaction(record))
        def _transaction_info():
            self.transaction_info(record)
        def _not_used():
            print "Didn't use record: %s" % (record,)

        rectypes = {
            '20' : _transmission_number,
            '25' : _account_number,
            '28' : _statement_number,
            '28C': _statement_number,
            '60F': _opening_balance,
            '62F': _closing_balance,
           #'64' : _forward_available,
           #'62M': _interim_balance,
            '61' : _transaction_new,
            '86' : _transaction_info,
            }

        rectypes.get(record['recordid'], _not_used)()

    def transaction_info(self, record):
        '''
        Add extra information to transaction
        '''
        # Additional information for previous transaction
        if len(self.transactions) < 1:
            raise_error('Received additional information for non existent transaction', record)

        transaction = self.transactions[-1]

        transaction.id = ','.join([record[k] for k in ['infoline{0}'.format(i) for i in range(1,5)] if record.has_key(k)])

def raise_error(message, line):
    raise osv.except_osv(_('Import error'),
        'Error in import:%s\n\n%s' % (message, line))

class parser_hsbc_mt940(models.parser):
    code = 'HSBC-MT940'
    name = _('HSBC Swift MT940 statement export')
    country_code = 'GB'
    doc = _('''\
            This format is available through
            the HSBC web interface.
            ''')

    def parse(self, data):
        result = []
        parser = HSBCParser()
        # Split into statements
        statements = [st for st in re.split('[\r\n]*(?=:20:)', data)]
        # Split by records
        statement_list = [re.split('[\r\n ]*(?=:\d\d[\w]?:)', st) for st in statements]

        for statement_lines in statement_list:
            stmnt = statement()
            records = [parser.parse_record(record) for record in statement_lines]
            [stmnt.import_record(r) for r in records if r is not None]


            if stmnt.is_valid():
                result.append(stmnt)
            else:
                print "Invalid Statement:"
                print records[0]

        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
