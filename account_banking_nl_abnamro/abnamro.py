# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>)
#                  2011 - 2013 Therp BV (<http://therp.nl>)
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

'''
This parser follows the Dutch Banking Tools specifications which are
empirically recreated in this module.

Dutch Banking Tools uses the concept of 'Afschrift' or Bank Statement.
Every transaction is bound to a Bank Statement. As such, this module generates
Bank Statements along with Bank Transactions.
'''
from openerp.addons.account_banking.parsers import models
from openerp.addons.account_banking.parsers.convert import str2date
from openerp.tools.translate import _
from openerp.osv import orm

import re
import csv

__all__ = ['parser']

bt = models.mem_bank_transaction


class transaction_message(object):
    '''
    A auxiliary class to validate and coerce read values
    '''
    attrnames = [
        'local_account', 'local_currency', 'date', 'u1', 'u2', 'date2',
        'transferred_amount', 'blob',
    ]

    def __init__(self, values, subno):
        '''
        Initialize own dict with attributes and coerce values to right type
        '''
        if len(self.attrnames) != len(values):
            raise ValueError(
                _('Invalid transaction line: expected %d columns, found '
                  '%d') % (len(self.attrnames), len(values))
            )
        #  Strip all values except the blob
        for (key, val) in zip(self.attrnames, values):
            self.__dict__[key] = key == 'blob' and val or val.strip()
        # for lack of a standardized locale function to parse amounts
        self.local_account = self.local_account.zfill(10)
        self.transferred_amount = float(
            self.transferred_amount.replace(',', '.'))
        self.execution_date = str2date(self.date, '%Y%m%d')
        self.value_date = str2date(self.date, '%Y%m%d')
        # Set statement_id based on week number
        self.statement_id = self.execution_date.strftime('%Yw%W')
        self.id = str(subno).zfill(4)


class transaction(models.mem_bank_transaction):
    '''
    Implementation of transaction communication class for account_banking.
    '''
    attrnames = ['local_account', 'local_currency', 'transferred_amount',
                 'blob', 'execution_date', 'value_date', 'id',
                 ]

    type_map = {
        # retrieved from online help in the Triodos banking application
        'BEA': bt.PAYMENT_TERMINAL,  # Pin
        'GEA': bt.BANK_TERMINAL,  # ATM
        'COSTS': bt.BANK_COSTS,
        'BANK': bt.ORDER,
        'GIRO': bt.ORDER,
        'INTL': bt.ORDER,  # international order
        'UNKN': bt.ORDER,  # everything else
        'SEPA': bt.ORDER,
        'PAYB': bt.PAYMENT_BATCH,
        'RETR': bt.STORNO,
    }

    def __init__(self, line, *args, **kwargs):
        '''
        Initialize own dict with read values.
        '''
        super(transaction, self).__init__(*args, **kwargs)
        # Copy attributes from auxiliary class to self.
        for attr in self.attrnames:
            setattr(self, attr, getattr(line, attr))
        # Initialize other attributes
        self.transfer_type = 'UNKN'
        self.remote_account = ''
        self.remote_owner = ''
        self.reference = ''
        self.message = ''
        # Decompose structured messages
        self.parse_message()

    def is_valid(self):
        if not self.error_message:
            if not self.transferred_amount:
                self.error_message = "No transferred amount"
            elif not self.execution_date:
                self.error_message = "No execution date"
            elif not self.remote_account and self.transfer_type not in [
                    'BEA', 'GEA', 'COSTS', 'UNKN', 'PAYB', ]:
                self.error_message = _(
                    'No remote account for transaction type %s'
                ) % self.transfer_type
        if self.error_message:
            raise orm.except_orm(_('Error !'), _(self.error_message))
        return not self.error_message

    def parse_message(self):
        '''
        Parse structured message parts into appropriate attributes
        '''
        def split_blob(line):
            # here we split up the blob, which the last field in a tab
            # separated statement line the blob is a *space separated* fixed
            # field format with field length 32. Empty fields are ignored
            col = 0
            size = 33
            res = []
            while(len(line) > col * size):
                separation = (col + 1) * size - 1
                if line[col * size: separation].strip():
                    part = line[col * size: separation]
                    # If the separation character is not a space, add it anyway
                    # presumably for sepa feedback strings only
                    if (len(line) > separation and line[separation] != ' '):
                        part += line[separation]
                    res.append(part)
                col += 1
            return res

        def get_sepa_dict(field):
            """
            Parses a subset of SEPA feedback strings as occur
            in this non-SEPA csv format.

            The string consists of slash separated KEY/VALUE pairs,
            but the slash is allowed to and known to occur in VALUE as well!
            """
            def _sepa_message(field, reason):
                return _(
                    'unable to parse SEPA string: %s - %s' % (field, reason))

            def _get_next_key(items, start):
                '''Find next key, starting from start, returns the key found,
                the start position in the array and the end position + 1'''
                known_keys = [
                    'TRTP', 'IBAN', 'BIC', 'NAME', 'RTRN', 'EREF', 'SWOC',
                    'REMI', 'ADDR', 'CPRP', 'CREF', 'CSID', 'ISDT', 'MARF',
                    'NRTX', 'NRTXR', 'PREF', 'PURP', 'REFOB', 'RREF', 'RTYP',
                    'SVCL', 'SWOD', 'BENM//ID', 'ORDP//ID', 'ORDP//RID',
                    'ORIG//CSID', 'ORIG//MARF', 'ULTD//NAME', 'ULTD//ID',
                    'ULTB//NAME', 'ULTB//ID'
                ]
                items_len = len(items)
                start_index = start
                # Search until start after end of items
                while start_index < items_len:
                    end_index = start_index + 1
                    while end_index < items_len:
                        key = '/'.join(items[start_index:end_index])
                        if key in known_keys:
                            return (key, start_index, end_index)
                        end_index += 1
                    start_index += 1
                return False

            items = field[1:].split('/')
            assert len(items) > 1, _sepa_message(field, _('too few items'))
            sepa_dict = {}
            item_index = 0
            items_len = len(items)
            key_info = _get_next_key(items, item_index)
            assert key_info, _sepa_message(
                field, _('no key found for start %d') % item_index)
            assert key_info[1] == 0, _sepa_message(
                field, _('invalid data found before key %s') % key_info[0])
            while key_info:
                sepa_key = key_info[0]
                item_index = key_info[2]
                # Find where next key - if any - starts
                key_info = _get_next_key(items, item_index)
                value_end_index = (key_info and key_info[1]) or items_len
                sepa_value = (
                    ((value_end_index > item_index) and
                     '/'.join(items[item_index:value_end_index])) or '')
                sepa_dict[sepa_key] = sepa_value
            return sepa_dict

        def parse_type(field):
            # here we process the first field, which identifies the statement
            # type and in case of certain types contains additional information
            transfer_type = 'UNKN'
            remote_account = False
            remote_owner = False
            if field.startswith('/TRTP/'):
                transfer_type = 'SEPA'
            elif field.startswith('GIRO '):
                transfer_type = 'GIRO'
                # field has markup 'GIRO ACCOUNT OWNER'
                # separated by clusters of space of varying size
                account_match = re.match(r'\s*([0-9]+)\s(.*)$', field[5:])
                if account_match:
                    remote_account = account_match.group(1).zfill(10)
                    remote_owner = account_match.group(2).strip() or ''
                else:
                    raise orm.except_orm(
                        _('Error !'),
                        _('unable to parse GIRO string: %s') % field)
            elif field.startswith('BEA '):
                transfer_type = 'BEA'
                # columns 6 to 16 contain the terminal identifier
                # column 17 contains a space
                # columns 18 to 31 contain date and time in DD.MM.YY/HH.MM
                # format
            elif field.startswith('GEA '):
                transfer_type = 'GEA'
                # columns 6 to 16 contain the terminal identifier
                # column 17 contains a space
                # columns 18 to 31 contain date and time in DD.MM.YY/HH.MM
                # format
            elif field.startswith('MAANDBIJDRAGE ABNAMRO'):
                transfer_type = 'COSTS'
            elif re.match(r"^\s([0-9]+\.){3}[0-9]+\s", field):
                transfer_type = 'BANK'
                remote_account = field[1:13].strip().replace('.', '').zfill(10)
                # column 14 to 31 is either empty or contains the remote owner
                remote_owner = field[14:32].strip()
            elif re.match("^EL[0-9]{13}I", field):
                transfer_type = 'INTL'
            elif field.startswith("TOTAAL BETALINGEN"):
                transfer_type = 'PAYB'
            return (transfer_type, remote_account, remote_owner)

        fields = split_blob(self.blob)
        (self.transfer_type, self.remote_account, self.remote_owner) = \
            parse_type(fields[0])

        if self.transfer_type == 'SEPA':
            sepa_dict = get_sepa_dict(''.join(fields))
            sepa_type = sepa_dict.get('TRTP') or ''
            self.transfer_type = {
                'SEPA BATCH': 'PAYB',
                'SEPA BATCH SALARIS': 'PAYB',
                'SEPA TERUGBOEKING': 'RETR',
            }.get(sepa_type.upper(), 'SEPA')
            self.remote_account = sepa_dict.get('IBAN', False)
            self.remote_bank_bic = sepa_dict.get('BIC', False)
            self.remote_owner = sepa_dict.get('NAME', False)
            self.reference = sepa_dict.get('REMI', '')

        # extract other information depending on type
        elif self.transfer_type == 'GIRO':
            if not self.remote_owner and len(fields) > 1:
                # OWNER is listed in the second field if not in the first
                self.remote_owner = fields[1].strip() or False
                fields = [fields[0]] + fields[2:]
            self.message = ' '.join(field.strip() for field in fields[1:])

        elif self.transfer_type == 'BEA':
            # second column contains remote owner and bank pass identification
            self.remote_owner = (
                len(fields) > 1 and fields[1].split(',')[0].strip() or False)
            # column 2 and up can contain additional messsages
            # (such as transaction costs or currency conversion)
            self.message = ' '.join(field.strip() for field in fields)

        elif self.transfer_type == 'BANK':
            # second column contains the remote owner or the first message line
            if not self.remote_owner:
                self.remote_owner = (
                    len(fields) > 1 and fields[1].strip() or False)
                self.message = ' '.join(field.strip() for field in fields[2:])
            else:
                self.message = ' '.join(field.strip() for field in fields[1:])

        elif self.transfer_type == 'INTL':
            # first column seems to consist of some kind of international
            # transaction id
            self.reference = fields[0].strip()
            # second column seems to contain remote currency and amount
            # to be processed in a later release of this module
            self.message = len(fields) > 1 and fields[1].strip() or False
            # third column contains iban, preceeded by a slash forward
            if len(fields) > 2:
                if fields[2].startswith('/'):
                    self.remote_account = fields[2][1:].strip()
                else:
                    self.remote_account = fields[2].strip()
                # fourth column contains remote owner
                self.remote_owner = (len(fields) > 3 and fields[3].strip() or
                                     False)
                self.message += ' ' + (
                    ' '.join(field.strip() for field in fields[4:]))

        else:
            self.message = ' '.join(field.strip() for field in fields)

        if not self.reference:
            # the reference is sometimes flagged by the prefix "BETALINGSKENM."
            # but can be any numeric line really
            for field in fields[1:]:
                m = re.match(
                    r"^\s*((BETALINGSKENM\.)|(ACCEPTGIRO))?\s*([0-9]+"
                    r"([ /][0-9]+)*)\s*$",
                    field)
                if m:
                    self.reference = m.group(4)
                    break


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
        self.date = str2date(msg.date, '%Y%m%d')
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
    code = 'ABNAM'
    country_code = 'NL'
    name = _('Abnamro (NL)')
    doc = _('''\
The Dutch Abnamro format is a tab separated text format. The last of these
fields is itself a fixed length array containing transaction type, remote
account and owner. The bank does not provide a formal specification of the
format. Transactions are not explicitely tied to bank statements, although
each file covers a period of two weeks.
''')

    def parse(self, cr, data):
        result = []
        stmnt = None
        lines = data.split('\n')
        # Transaction lines are not numbered, so keep a tracer
        subno = 0
        statement_id = False
        for line in csv.reader(lines, delimiter='\t', quoting=csv.QUOTE_NONE):
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
