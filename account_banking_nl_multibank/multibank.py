# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
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
from account_banking.sepa import postalcode
from tools.translate import _
import csv

__all__ = ['parser']

bt = models.mem_bank_transaction


class transaction_message(object):
    '''
    A auxiliary class to validate and coerce read values
    '''
    attrnames = [
        'date', 'local_account', 'remote_account', 'remote_owner', 'u1', 'u2',
        'u3', 'local_currency', 'start_balance', 'remote_currency',
        'transferred_amount', 'execution_date', 'value_date', 'nr1',
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
        if len(accountno) == 10:  # Invalid: longest number is 9
            accountno = accountno[1:]
        # 9-scheme or 7-scheme?
        stripped = accountno.lstrip('0')
        if len(stripped) <= 7:
            accountno = stripped
        return accountno

    def __init__(self, values, subno):
        '''
        Initialize own dict with attributes and coerce values to right type
        '''
        if len(self.attrnames) != len(values):
            raise ValueError(
                _('Invalid transaction line: expected %d columns, found %d')
                % (len(self.attrnames), len(values))
            )
        self.__dict__.update(dict(zip(self.attrnames, values)))
        self.start_balance = float(self.start_balance)
        self.transferred_amount = float(self.transferred_amount)
        self.execution_date = str2date(self.execution_date, '%d-%m-%Y')
        self.value_date = str2date(self.value_date, '%d-%m-%Y')
        self.id = str(subno).zfill(4)


class transaction(models.mem_bank_transaction):
    '''
    Implementation of transaction communication class for account_banking.
    '''
    attrnames = ['local_account', 'local_currency', 'remote_account',
                 'remote_owner', 'remote_currency', 'transferred_amount',
                 'execution_date', 'value_date', 'transfer_type',
                 'reference', 'message', 'statement_id', 'id',
                 ]

    type_map = {
        'ACC': bt.ORDER,
        'BEA': bt.PAYMENT_TERMINAL,
        'BTL': bt.ORDER,
        'DIV': bt.ORDER,
        'IDB': bt.PAYMENT_TERMINAL,
        'INC': bt.DIRECT_DEBIT,
        'IOB': bt.ORDER,
        'KNT': bt.BANK_COSTS,
        'KST': bt.BANK_COSTS,
        'OPN': bt.BANK_TERMINAL,
        'OVS': bt.ORDER,
        'PRV': bt.BANK_COSTS,
        'TEL': bt.ORDER,
    }

    def __init__(self, line, *args, **kwargs):
        '''
        Initialize own dict with read values.
        '''
        super(transaction, self).__init__(*args, **kwargs)
        # Copy attributes from auxiliary class to self.
        for attr in self.attrnames:
            setattr(self, attr, getattr(line, attr))
        # Decompose structured messages
        self.parse_message()
        # Set reference when bank costs
        if self.type == bt.BANK_COSTS:
            self.reference = self.message[:32].rstrip()

    def is_valid(self):
        '''
        There are a few situations that can be signaled as 'invalid' but are
        valid nontheless:

        1. Transfers from one account to another under the same account holder
        get not always a remote_account and remote_owner. They have their
        transfer_type set to 'PRV'.

        2. Invoices from the bank itself are communicated through statements.
        These too have no remote_account and no remote_owner. They have a
        transfer_type set to 'KST', 'KNT' or 'DIV'.

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
        return ((
            self.transferred_amount and self.execution_date
            and self.value_date)
            and (self.remote_account or self.transfer_type in [
                'KST', 'PRV', 'BTL', 'BEA', 'OPN', 'KNT', 'DIV'
            ] and not self.error_message))

    def parse_message(self):
        '''
        Parse structured message parts into appropriate attributes
        '''
        if self.transfer_type == 'ACC':
            # Accept Giro - structured message payment
            # First part of message is redundant information - strip it
            msg = self.message[self.message.index('navraagnr.'):]
            self.message = ' '.join(msg.split())

        elif self.transfer_type == 'BEA':
            # Payment through payment terminal
            # Remote owner is part of message, while remote_owner is set
            # to the intermediate party, which we don't need.
            self.remote_owner = self.message[:23].rstrip()
            self.remote_owner_city = self.message[23:31].rstrip()
            self.message = self.message[31:]

        elif self.transfer_type == 'BTL':
            # International transfers.
            # Remote party is encoded in message, including bank costs
            parts = self.message.split('  ')
            last = False
            for part in parts:
                if part.startswith('bedrag. '):
                    # The ordered transferred amount
                    currency, amount = part.split('. ')[1].split()
                    if self.remote_currency != currency.upper():
                        self.error_message = (
                            'Remote currency in message differs from '
                            'transaction.'
                        )
                    else:
                        self.local_amount = float(amount)
                elif part.startswith('koers. '):
                    # The currency rate used
                    self.exchange_rate = float(part.split('. ')[1])
                elif part.startswith('transfer prov. '):
                    # The provision taken by the bank
                    # Note that the amount must be negated to get the right
                    # direction
                    currency, costs = part.split('. ')[1].split()
                    self.provision_costs = -float(costs)
                    self.provision_costs_currency = currency.upper()
                    self.provision_costs_description = 'Transfer costs'
                elif part.startswith('aan. '):
                    # The remote owner
                    self.remote_owner = part.replace('aan. ', '').rstrip()
                    last = True
                elif last:
                    # Last parts are address lines
                    address = part.rstrip()
                    iso, pc, city = postalcode.split(address)
                    if pc and city:
                        self.remote_owner_postalcode = pc
                        self.remote_owner_city = city.strip()
                        self.remote_owner_country_code = iso
                    else:
                        self.remote_owner_address.append(address)

        elif self.transfer_type == 'DIV':
            # A diverse transfer. Message can be anything, but has some
            # structure
            ptr = self.message.find(self.reference)
            if ptr > 0:
                address = self.message[:ptr].rstrip().split('  ')
                length = len(address)
                if length >= 1:
                    self.remote_owner = address[0]
                if length >= 2:
                    self.remote_owner_address.append(address[1])
                if length >= 3:
                    self.remote_owner_city = address[2]
                self.message = self.message[ptr:].rstrip()
            if self.message.find('transactiedatum') >= 0:
                rest = self.message.split('transactiedatum')
                if rest[1].startswith('* '):
                    self.execution_date = str2date(rest[1][2:], '%d-%m-%Y')
                else:
                    self.execution_date = str2date(rest[1][2:], '%d %m %Y')
                self.message = rest[0].rstrip()

        elif self.transfer_type == 'IDB':
            # Payment by iDeal transaction
            # Remote owner can be part of message, while remote_owner can be
            # set to the intermediate party, which we don't need.
            parts = self.message.split('  ')
            # Second part: structured id, date & time
            subparts = parts[1].split()
            datestr = '-'.join(subparts[1:4])
            timestr = ':'.join(subparts[4:])
            parts[1] = ' '.join([subparts[0], datestr, timestr])
            # Only replace reference when redundant
            if self.reference == parts[0]:
                if parts[2]:
                    self.reference = ' '.join([parts[2], datestr, timestr])
                else:
                    self.reference += ' '.join([datestr, timestr])
            # Optional fourth path contains remote owners name
            if len(parts) > 3 and parts[-1].find(self.remote_owner) < 0:
                self.remote_owner = parts[-1].rstrip()
                parts = parts[:-1]
            self.message = ' '.join(parts)


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
    country_code = 'NL'
    name = _('Dutch Banking Tools')
    doc = _('''\
The Dutch Banking Tools format is basicly a MS Excel CSV format.
There are two sub formats: MS Excel format and MS-Excel 2004 format.
Both formats are covered with this parser. All transactions are tied
to Bank Statements.
''')

    def parse(self, cr, data):
        result = []
        stmnt = None
        dialect = csv.excel()
        dialect.quotechar = '"'
        dialect.delimiter = ';'
        lines = data.split('\n')
        # Probe first record to find out which format we are parsing.
        if lines and lines[0].count(',') > lines[0].count(';'):
            dialect.delimiter = ','
        if lines and lines[0].count("'") > lines[0].count('"'):
            dialect.quotechar = "'"
        # Transaction lines are not numbered, so keep a tracer
        subno = 0
        for line in csv.reader(lines, dialect=dialect):
            # Skip empty (last) lines
            if not line:
                continue
            subno += 1
            msg = transaction_message(line, subno)
            if stmnt and stmnt.id != msg.statement_id:
                result.append(stmnt)
                stmnt = None
                subno = 0
            if not stmnt:
                stmnt = statement(msg)
            else:
                stmnt.import_transaction(msg)
        result.append(stmnt)
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
