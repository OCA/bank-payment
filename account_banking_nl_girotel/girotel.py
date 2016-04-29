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
This parser follows the Dutch Girotel specifications which are
empirically recreated in this module.
There is very little information for validating the format or the content
within.

Dutch Girotel uses no concept of 'Afschrift' or Bank Statement.
To overcome a lot of problems, this module generates reproducible Bank
Staments per months period.

Transaction ID's are missing, but generated on the fly based on transaction
date and sequence position therein.

Assumptions:
    1. transactions are sorted in ascending order of date.
    2. new transactions are appended after previously known transactions of
       the same date
    3. banks maintain order in transaction lists within a single date
    4. the data comes from the SWIFT-network (limited ASCII)

Assumption 4 seems not always true, leading to wrong character conversions.
As a counter measure, all imported data is converted to SWIFT-format before
usage.
'''
from account_banking.parsers import models
from account_banking.parsers.convert import str2date, to_swift
from tools.translate import _
import re
import csv

bt = models.mem_bank_transaction

__all__ = ['parser']


class transaction_message(object):
    '''
    A auxiliary class to validate and coerce read values
    '''
    attrnames = [
        'local_account', 'date', 'transfer_type', 'u1',
        'remote_account', 'remote_owner', 'u2', 'transferred_amount',
        'direction', 'u3', 'message', 'remote_currency',
    ]
    # Attributes with possible non-ASCII string content
    strattrs = [
        'remote_owner', 'message'
    ]

    ids = {}

    def __setattribute__(self, attr, value):
        '''
        Convert values for string content to SWIFT-allowable content
        '''
        if attr != 'strattrs' and attr in self.strattrs:
            value = to_swift(value)
        super(transaction_message, self).__setattribute__(attr, value)

    def __getattribute__(self, attr):
        '''
        Convert values from string content to SWIFT-allowable content
        '''
        retval = super(transaction_message, self).__getattribute__(attr)
        return attr != (
            'strattrs' and attr in self.strattrs and to_swift(retval) or retval
        )

    def genid(self):
        '''
        Generate a new id when not assigned before
        '''
        if (not hasattr(self, 'id')) or not self.id:
            if self.date in self.ids:
                self.ids[self.date] += 1
            else:
                self.ids[self.date] = 1
            self.id = self.date.strftime('%%Y%%m%%d%04d' % self.ids[self.date])

    def __init__(self, values):
        '''
        Initialize own dict with attributes and coerce values to right type
        '''
        if len(self.attrnames) != len(values):
            raise ValueError(
                _('Invalid transaction line: expected %d columns, found %d')
                % (len(self.attrnames), len(values))
            )
        self.__dict__.update(dict(zip(self.attrnames, values)))
        self.date = str2date(self.date, '%Y%m%d')
        if self.direction == 'A':
            self.transferred_amount = -float(self.transferred_amount)
            # payment batch done via clieop
            if (self.transfer_type == 'VZ' and
                    (not self.remote_account or self.remote_account == '0') and
                    (not self.message or re.match(r'^\s*$', self.message)) and
                    self.remote_owner.startswith('TOTAAL ')):
                self.transfer_type = 'PB'
                self.message = self.remote_owner
                self.remove_owner = False
            # payment batch done via sepa
            if self.transfer_type == 'VZ'\
                    and not self.remote_account\
                    and not self.remote_owner\
                    and re.match(
                        r'^Verzamel Eurobetaling .* TOTAAL \d+ POSTEN\s*$',
                        self.message):
                self.transfer_type = 'PB'
        else:
            self.transferred_amount = float(self.transferred_amount)
        self.local_account = self.local_account.zfill(10)
        if self.transfer_type != 'DV':
            self.remote_account = self.remote_account.zfill(10)
        else:
            self.remote_account = False
        self.execution_date = self.value_date = self.date
        self.remote_owner = self.remote_owner.rstrip()
        self.message = self.message.rstrip()
        self.genid()

    @property
    def statement_id(self):
        '''Return calculated statement id'''
        return self.id[:6]


class transaction(models.mem_bank_transaction):
    '''
    Implementation of transaction communication class for account_banking.
    '''
    attrnames = ['statement_id', 'remote_account', 'remote_owner',
                 'remote_currency', 'transferred_amount', 'execution_date',
                 'value_date', 'transfer_type', 'message',
                 ]

    type_map = {
        'BA': bt.PAYMENT_TERMINAL,
        'BT': bt.ORDER,
        'DV': bt.BANK_COSTS,
        'GM': bt.BANK_TERMINAL,
        'GT': bt.ORDER,
        'IC': bt.DIRECT_DEBIT,
        'OV': bt.ORDER,
        'VZ': bt.ORDER,
        'PB': bt.PAYMENT_BATCH,
    }

    def __init__(self, line, *args, **kwargs):
        '''
        Initialize own dict with read values.
        '''
        super(transaction, self).__init__(*args, **kwargs)
        for attr in self.attrnames:
            setattr(self, attr, getattr(line, attr))
        self.id = line.id.replace(line.statement_id, '')
        self.reference = self.message[:32].rstrip()
        self.parse_message()

    def is_valid(self):
        '''
        There are a few situations that can be signaled as 'invalid' but are
        valid nontheless:
        1. Invoices from the bank itself are communicated through statements.
        These too have no remote_account and no remote_owner. They have a
        transfer_type set to 'DV'.
        2. Transfers sent through the 'International Transfers' system get
        their feedback rerouted through a statement, which is not designed to
        hold the extra fields needed. These transfers have their transfer_type
        set to 'BT'.
        3. Cash payments with debit cards are not seen as a transfer between
        accounts, but as a cash withdrawal. These withdrawals have their
        transfer_type set to 'BA'.
        4. Cash withdrawals from banks are too not seen as a transfer between
        two accounts - the cash exits the banking system. These withdrawals
        have their transfer_type set to 'GM'.
        5. Aggregated payment batches. These transactions have transfer type
        'VZ' natively but are changed to 'PB' while parsing. These transactions
        have no remote account.
        '''
        return bool(self.transferred_amount and self.execution_date and (
                    self.remote_account or
                    self.transfer_type in [
                        'DV', 'PB', 'BT', 'BA', 'GM',
                    ]))

    def refold_message(self, message):
        '''
        Refold a previously chopped and fixed length message back into one
        line
        '''
        msg, message = message.rstrip(), None
        parts = [msg[i:i + 32].rstrip() for i in range(0, len(msg), 32)]
        return '\n'.join(parts)

    def parse_message(self):
        '''
        Parse the message as sent by the bank. Most messages are composed
        of chunks of 32 characters, but there are exceptions.
        '''
        if self.transfer_type == 'VZ':
            # Credit bank costs (interest) gets a special treatment.
            if self.remote_owner.startswith('RC AFREK.  REK. '):
                self.transfer_type = 'DV'

        if self.transfer_type == 'DV':
            # Bank costs.
            # Title of action is in remote_owner, message contains additional
            # info
            self.reference = self.remote_owner.rstrip()
            parts = [self.message[i:i + 32].rstrip()
                     for i in range(0, len(self.message), 32)
                     ]
            if len(parts) > 3:
                self.reference = parts[-1]
                self.message = '\n'.join(parts[:-1])
            else:
                self.message = '\n'.join(parts)
            self.remote_owner = ''

        elif self.transfer_type == 'BA':
            # Payment through bank terminal
            # Id of terminal and some owner info is part of message
            if self.execution_date < str2date('20091130', '%Y%m%d'):
                parts = self.remote_owner.split('>')
            else:
                parts = self.remote_owner.split('>\\')
            self.remote_owner = ' '.join(parts[0].split()[1:])
            if len(parts) > 1 and len(parts[1]) > 2:
                self.remote_owner_city = parts[1]
            self.message = self.refold_message(self.message)
            self.reference = '%s %s' % (self.remote_owner,
                                        ' '.join(self.message.split()[2:4])
                                        )

        elif self.transfer_type == 'IC':
            # Direct debit - remote_owner containts reference, while
            # remote_owner is part of the message, most often as
            # first part of the message.
            # Sometimes this misfires, as with the tax office collecting road
            # taxes, but then a once-only manual correction is sufficient.
            parts = [self.message[i:i + 32].rstrip()
                     for i in range(0, len(self.message), 32)
                     ]
            self.reference = self.remote_owner

            if not parts:
                return

            if self.reference.startswith('KN: '):
                self.reference = self.reference[4:]
                if parts[0] == self.reference:
                    parts = parts[1:]
            # The tax administration office seems to be the notorious exception
            # to the rule
            if parts[-1] == 'BELASTINGDIENST':
                self.remote_owner = parts[-1].capitalize()
                parts = parts[:-1]
            else:
                self.remote_owner = parts[0]
                parts = parts[1:]
            # Leave the message, to assist in manual correction of misfires
            self.message = '\n'.join(parts)

        elif self.transfer_type == 'GM':
            # Cash withdrawal from a bank terminal
            # Structured remote_owner message containing bank info and location
            if self.remote_owner.startswith('OPL. CHIPKNIP'):
                # Transferring cash to debit card
                self.remote_account = self.local_account
                self.message = '%s: %s' % (self.remote_owner, self.message)
            else:
                if self.execution_date < str2date('20091130', '%Y%m%d'):
                    parts = self.remote_owner.split('>')
                else:
                    parts = self.remote_owner.split('>\\')
                if len(parts) > 1:
                    self.reference = ' '.join([x.rstrip() for x in parts])
                else:
                    self.reference = 'ING BANK NV %s' % parts[0].split('  ')[0]
            self.remote_owner = ''

        elif self.transfer_type == 'GT':
            # Normal transaction, but remote_owner can contain city, depending
            # on length of total. As there is no clear pattern, leave it as
            # is.
            self.message = self.refold_message(self.message)

        else:
            # Final default: reconstruct message from chopped fixed length
            # message parts.
            self.message = self.refold_message(self.message)


class statement(models.mem_bank_statement):
    '''
    Implementation of bank_statement communication class of account_banking
    '''
    def __init__(self, msg, start_balance=0.0, *args, **kwargs):
        '''
        Set decent start values based on first transaction read
        '''
        super(statement, self).__init__(*args, **kwargs)
        self.id = msg.statement_id
        self.local_account = msg.local_account
        self.date = msg.date
        self.start_balance = self.end_balance = start_balance
        self.import_transaction(msg)

    def import_transaction(self, msg):
        '''
        Import a transaction and keep some house holding in the mean time.
        '''
        trans = transaction(msg)
        self.end_balance += trans.transferred_amount
        self.transactions.append(trans)


class parser(models.parser):
    code = 'NLGT'
    name = _('Dutch Girotel - Kommagescheiden')
    country_code = 'NL'
    doc = _('''\
The Dutch Girotel - Kommagescheiden format is basicly a MS Excel CSV format.
''')

    def parse(self, cr, data):
        result = []
        stmnt = None
        dialect = csv.excel()
        dialect.quotechar = '"'
        dialect.delimiter = ','
        lines = data.split('\n')
        start_balance = 0.0
        for line in csv.reader(lines, dialect=dialect):
            # Skip empty (last) lines
            if not line:
                continue
            msg = transaction_message(line)
            if stmnt and stmnt.id != msg.statement_id:
                start_balance = stmnt.end_balance
                result.append(stmnt)
                stmnt = None
            if not stmnt:
                stmnt = statement(msg, start_balance=start_balance)
            else:
                stmnt.import_transaction(msg)
        result.append(stmnt)
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
