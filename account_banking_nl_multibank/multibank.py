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
import csv

__all__ = ['parser']

class transaction_message(object):
    '''
    A auxiliary class to validate and coerce read values
    '''
    attrnames = [
        'date', 'local_account', 'remote_account', 'remote_owner', 'u1', 'u2',
        'u3', 'local_currency', 'start_balance', 'remote_currency',
        'transferred_amount', 'execution_date', 'effective_date', 'nr1',
        'transfer_type', 'nr2', 'reference', 'message', 'statement_id'
    ]

    @staticmethod
    def clean_account(accountno):
        '''
        There seems to be some SEPA movement in data: account numbers
        get prefixed by zeroes as in BBAN. Convert those to 'old' local
        account numbers

        Edit: All account number now follow the BBAN scheme. As SNS Bank,
        from which this module was re-engineered, follows the Dutch
        Banking Tools regulations, it is considered to be used by all banks
        in the Netherlands which comply to it. If not, please notify us.
        '''
        if len(accountno) == 10: # Invalid: longest number is 9
            accountno = accountno[1:]
        # 9-scheme or 7-scheme?
        stripped = accountno.lstrip('0')
        if len(stripped) <= 7:
            accountno = stripped
        return accountno

    def __init__(self, values):
        '''
        Initialize own dict with attributes and coerce values to right type
        '''
        self.__dict__.update(dict(zip(self.attrnames, values)))
        #self.local_account = self.clean_account(self.local_account)
        #self.remote_account = self.clean_account(self.remote_account)
        self.start_balance = float(self.start_balance)
        self.transferred_amount = float(self.transferred_amount)
        self.execution_date = str2date(self.execution_date, '%d-%m-%Y')
        self.effective_date = str2date(self.effective_date, '%d-%m-%Y')

class transaction(models.mem_bank_transaction):
    '''
    Implementation of transaction communication class for account_banking.
    '''
    attrnames = ['remote_account', 'remote_currency', 'transferred_amount',
                 'execution_date', 'effective_date', 'transfer_type',
                 'reference', 'message'
                ]

    def __init__(self, line, *args, **kwargs):
        '''
        Initialize own dict with read values.
        '''
        super(transaction, self).__init__(*args, **kwargs)
        for attr in self.attrnames:
            setattr(self, attr, getattr(line, attr))

    def is_valid(self):
        '''
        There are a few situations that can be signaled as 'invalid' but are
        valid nontheless:
        1. Transfers from one account to another under the same account holder
        get not always a remote_account and remote_owner. They have their
        transfer_type set to 'PRV'.
        2. Invoices from the bank itself are communicated through statements.
        These too have no remote_account and no remote_owner. They have a
        transfer_type set to 'KST'.
        3. Transfers sent through the 'International Transfers' system get
        their feedback rerouted through a statement, which is not designed to
        hold the extra fields needed. These transfers have their transfer_type
        set to 'BTL'.
        4. Cash payments with debit cards are not seen as a transfer between
        accounts, but as a cash withdrawal. These withdrawals have their
        transfer_type set to 'BEA'.
        5. Cash withdrawals from banks are too not seen as a transfer between
        two accounts - the cash exits the banking system. These withdrawals
        have their transfer_type set to 'OPN'.
        '''
        return (self.transferred_amount and self.execution_date and
                self.effective_date) and (
                    self.remote_account or
                    self.transfer_type in [
                        'KST', 'PRV', 'BTL', 'BEA', 'OPN'
                    ])

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
        self.start_balance = self.end_balance = msg.start_balance
        self.import_transaction(msg)

    def import_transaction(self, msg):
        '''
        Import a transaction and keep some house holding in the mean time.
        '''
        trans = transaction(msg)
        self.end_balance += trans.transferred_amount
        self.transactions.append(trans)

class parser(models.parser):
    code = 'NLBT'
    name = _('Dutch Banking Tools')
    doc = _('''\
The Dutch Banking Tools format is basicly a MS Excel CSV format.
There are two sub formats: MS Excel format and MS-Excel 2004 format.
Both formats are covered with this parser. All transactions are tied
to Bank Statements.
''')

    def parse(self, data):
        result = []
        stmnt = None
        dialect = csv.excel()
        dialect.quotechar = '"'
        dialect.delimiter = ';'
        lines = data.split('\n')
        # Probe first record to find out which format we are parsing.
        if lines and lines[0].count(',') > lines[0].count(';'):
            dialect.delimiter = ','
            dialect.quotechar = "'"
        for line in csv.reader(lines, dialect=dialect):
            # Skip empty (last) lines
            if not line:
                continue
            msg = transaction_message(line)
            if stmnt and stmnt.id != msg.statement_id:
                result.append(stmnt)
                stmnt = None
            if not stmnt:
                stmnt = statement(msg)
            else:
                stmnt.import_transaction(msg)
        result.append(stmnt)
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
