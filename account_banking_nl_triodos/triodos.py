# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>),
#                  2011 Therp BV (<http://therp.nl>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

'''
This parser follows the Dutch Banking Tools specifications which are
empirically recreated in this module.

Dutch Banking Tools uses the concept of 'Afschrift' or Bank Statement.
Every transaction is bound to a Bank Statement. As such, this module generates
Bank Statements along with Bank Transactions.
'''

from account_banking.parsers import models
from account_banking.parsers.convert import str2date
from tools.translate import _

import re
import csv

__all__ = ['parser']

bt = models.mem_bank_transaction


class transaction_message(object):
    '''
    A auxiliary class to validate and coerce read values
    '''
    attrnames = [
        'date', 'local_account', 'transferred_amount', 'debcred',
        'remote_owner', 'remote_account', 'transfer_type', 'reference',
    ]

    def __init__(self, values, subno):
        '''
        Initialize own dict with attributes and coerce values to right type
        '''
        if len(self.attrnames) != len(values):
            raise ValueError(
                _('Invalid transaction line: expected %d columns, found %d')
                % (len(self.attrnames), len(values)))
        self.__dict__.update(dict(zip(self.attrnames, values)))
        # for lack of a standardized locale function to parse amounts
        self.transferred_amount = float(
            re.sub(',', '.', re.sub(r'\.', '', self.transferred_amount)))
        if self.debcred == 'Debet':
            self.transferred_amount = -self.transferred_amount
        self.execution_date = str2date(self.date, '%d-%m-%Y')
        self.value_date = str2date(self.date, '%d-%m-%Y')
        self.statement_id = ''
        self.id = str(subno).zfill(4)
        # Normalize basic account numbers
        self.remote_account = self.remote_account.replace('.', '').zfill(10)
        self.local_account = self.local_account.replace('.', '').zfill(10)


class transaction(models.mem_bank_transaction):
    '''
    Implementation of transaction communication class for account_banking.
    '''
    attrnames = [
        'local_account',
        'remote_account',
        'remote_owner',
        'transferred_amount',
        'execution_date',
        'value_date',
        'transfer_type',
        'reference',
        'id',
    ]

    type_map = {
        # retrieved from online help in the Triodos banking application
        'AC': bt.ORDER,  # Acceptgiro gecodeerd
        'AN': bt.ORDER,  # Acceptgiro ongecodeerd
        'AT': bt.ORDER,  # Acceptgiro via internet
        'BA': bt.PAYMENT_TERMINAL,  # Betaalautomaat
        'CHIP': bt.BANK_TERMINAL,  # Chipknip
        # 'CO':  # Correctie
        'DB': bt.ORDER,  # Diskettebetaling
        # 'DV':  # Dividend
        'EI': bt.DIRECT_DEBIT,  # Europese Incasso
        'EICO': bt.DIRECT_DEBIT,  # Europese Incasso Correctie
        'EIST': bt.ORDER,  # Europese Incasso Storno
        'ET': bt.ORDER,  # Europese Transactie
        'ETST': bt.ORDER,  # Europese Transactie Storno
        'GA': bt.BANK_TERMINAL,  # Geldautomaat
        'IB': bt.ORDER,  # Interne Boeking
        'IC': bt.DIRECT_DEBIT,  # Incasso
        'ID': bt.ORDER,  # iDeal-betaling
        'IT': bt.ORDER,  # Internet transactie
        'KN': bt.BANK_COSTS,  # Kosten
        'KO': bt.BANK_TERMINAL,  # Kasopname
        # 'KS':  # Kwaliteitsstoring
        'OV': bt.ORDER,  # Overboeking. NB: can also be bt.BANK_COSTS
                         # when no remote_account specified!
        'PO': bt.ORDER,  # Periodieke Overboeking
        'PR': bt.BANK_COSTS,  # Provisie
        # 'RE':  # Rente
        # 'RS':  # Renteschenking
        'ST': bt.ORDER,  # Storno
        'TG': bt.ORDER,  # Telegiro
        # 'VL':  # Vaste Lening
        'VO': bt.DIRECT_DEBIT,  # Vordering overheid
        'VV': bt.ORDER,  # Vreemde valuta
    }

    def __init__(self, line, *args, **kwargs):
        '''
        Initialize own dict with read values.
        '''
        super(transaction, self).__init__(*args, **kwargs)
        # Copy attributes from auxiliary class to self.
        for attr in self.attrnames:
            setattr(self, attr, getattr(line, attr))
        self.message = ''
        # Decompose structured messages
        self.parse_message()
        if (self.transfer_type == 'OV' and
                not self.remote_account and
                not self.remote_owner):
            self.transfer_type = 'KN'

    def is_valid(self):
        if not self.error_message:
            if not self.transferred_amount:
                self.error_message = "No transferred amount"
            elif not self.execution_date:
                self.error_message = "No execution date"
            elif not self.remote_account and self.transfer_type not in [
                    'KN', 'TG', 'GA', 'BA', 'CHIP']:
                self.error_message = (
                    "No remote account for transaction type %s" %
                    self.transfer_type)
        return not self.error_message

    def parse_message(self):
        '''
        Parse structured message parts into appropriate attributes.
        '''
        # IBAN accounts are prefixed by BIC
        if self.remote_account:
            parts = self.remote_account.split(' ')
            if len(parts) == 2:
                self.remote_bank_bic = parts[0]
                self.remote_account = parts[1]


class statement(models.mem_bank_statement):
    '''
    Implementation of bank_statement communication class of account_banking
    '''
    def __init__(self, msg, *args, **kwargs):
        '''
        Set decent start values based on first transaction read
        '''
        super(statement, self).__init__(*args, **kwargs)
        self.id = msg.statement_id
        self.local_account = msg.local_account
        self.date = str2date(msg.date, '%d-%m-%Y')
        self.start_balance = self.end_balance = 0  # msg.start_balance
        self.import_transaction(msg)

    def import_transaction(self, msg):
        '''
        Import a transaction and keep some house holding in the mean time.
        '''
        trans = transaction(msg)
        self.end_balance += trans.transferred_amount
        self.transactions.append(trans)


class parser(models.parser):
    code = 'TRIOD'
    country_code = 'NL'
    name = _('Triodos Bank')
    doc = _('''\
The Dutch Triodos format is basicly a MS Excel CSV format. It is specifically
distinct from the Dutch multibank format. Transactions are not tied to Bank
Statements.
''')

    def parse(self, cr, data):
        result = []
        stmnt = None
        dialect = csv.excel()
        dialect.quotechar = '"'
        dialect.delimiter = ','
        lines = data.split('\n')
        # Transaction lines are not numbered, so keep a tracer
        subno = 0
        # fixed statement id based on import timestamp
        statement_id = False
        for line in csv.reader(lines, dialect=dialect):
            # Skip empty (last) lines
            if not line:
                continue
            subno += 1
            msg = transaction_message(line, subno)
            if not statement_id:
                statement_id = self.get_unique_statement_id(
                    cr, msg.execution_date.strftime('%Yw%W'))
            msg.statement_id = statement_id
            if stmnt:
                stmnt.import_transaction(msg)
            else:
                stmnt = statement(msg)
        result.append(stmnt)
        return result
