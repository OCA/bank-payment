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
from mt940_parser import HSBCParser
import re
import logging

bt = models.mem_bank_transaction
logger = logging.getLogger('hsbc_mt940')

from openerp.tools.translate import _
from openerp.osv import orm


def record2float(record, value):
    if record['creditmarker'][-1] == 'C':
        return float(record[value])
    return -float(record[value])


class transaction(models.mem_bank_transaction):

    mapping = {
        'execution_date': 'valuedate',
        'value_date': 'valuedate',
        'local_currency': 'currency',
        'transfer_type': 'bookingcode',
        'reference': 'custrefno',
        'message': 'furtherinfo'
    }

    type_map = {
        'NTRF': bt.ORDER,
        'NMSC': bt.ORDER,
        'NPAY': bt.PAYMENT_BATCH,
        'NCHK': bt.CHECK,
    }

    def __init__(self, record, *args, **kwargs):
        '''
        Transaction creation
        '''
        super(transaction, self).__init__(*args, **kwargs)
        for key, value in self.mapping.iteritems():
            if value in record:
                setattr(self, key, record[value])

        self.transferred_amount = record2float(record, 'amount')

        # Set the transfer type based on the bookingcode
        if record.get('bookingcode', 'ignore') in self.type_map:
            self.transfer_type = self.type_map[record['bookingcode']]
        else:
            # Default to the generic order, so it will be eligible for matching
            self.transfer_type = bt.ORDER

        if not self.is_valid():
            logger.info("Invalid: %s", record)

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
            self.local_account = (
                record['sortcode'] + ' ' + record['accnum'].zfill(8)
            )

        def _statement_number():
            self.id = '-'.join(
                [self.id, self.local_account, record['statementnr']]
            )

        def _opening_balance():
            self.start_balance = record2float(record, 'startingbalance')
            self.local_currency = record['currencycode']

        def _closing_balance():
            self.end_balance = record2float(record, 'endingbalance')
            self.date = record['bookingdate']

        def _transaction_new():
            self.transactions.append(transaction(record))

        def _transaction_info():
            self.transaction_info(record)

        def _not_used():
            logger.info("Didn't use record: %s", record)

        rectypes = {
            '20': _transmission_number,
            '25': _account_number,
            '28': _statement_number,
            '28C': _statement_number,
            '60F': _opening_balance,
            '62F': _closing_balance,
            '61': _transaction_new,
            '86': _transaction_info,
            }

        rectypes.get(record['recordid'], _not_used)()

    def transaction_info(self, record):
        '''
        Add extra information to transaction
        '''
        # Additional information for previous transaction
        if len(self.transactions) < 1:
            logger.info(
                "Received additional information for non existent transaction:"
            )
            logger.info(record)
        else:
            transaction = self.transactions[-1]
            transaction.id = ','.join((
                record[k]
                for k in (
                    'infoline{0}'.format(i)
                    for i in range(2, 5)
                )
                if k in record
            ))


def raise_error(message, line):
    raise orm.except_orm(
        _('Import error'),
        _('Error in import:') + '\n\n'.join((message, line))
    )


class parser_hsbc_mt940(models.parser):
    code = 'HSBC-MT940'
    name = _('HSBC Swift MT940 statement export')
    country_code = 'GB'
    doc = _('''\
            This format is available through
            the HSBC web interface.
            ''')

    def parse(self, cr, data):
        result = []
        parser = HSBCParser()
        # Split into statements
        statements = [st for st in re.split('[\r\n]*(?=:20:)', data)]
        # Split by records
        statement_list = [
            re.split('[\r\n ]*(?=:\d\d[\w]?:)', st)
            for st in statements
        ]

        for statement_lines in statement_list:
            stmnt = statement()
            records = [
                parser.parse_record(record)
                for record in statement_lines
            ]
            [stmnt.import_record(r) for r in records if r is not None]

            if stmnt.is_valid():
                result.append(stmnt)
            else:
                logger.info("Invalid Statement:")
                logger.info(records[0])

        return result
