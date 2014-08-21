# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Smile (<http://smile.fr>).
#    Copyright (C) 2011 Therp BV (<http://therp.nl>).
#
#    Based on the multibank module by EduSense BV
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>),
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

from openerp.addons.account_banking.parsers import models
from openerp.addons.account_banking.parsers.convert import str2date
from openerp.tools.translate import _

import re
import csv

__all__ = ['parser']

bt = models.mem_bank_transaction

"""
First line states the legend
"Datum","Naam / Omschrijving","Rekening","Tegenrekening","Code","Af Bij",\
"Bedrag (EUR)","MutatieSoort","Mededelingen

"""


class transaction_message(object):
    '''
    A auxiliary class to validate and coerce read values
    '''
    attrnames = [
        'date', 'remote_owner', 'local_account', 'remote_account',
        'transfer_type', 'debcred', 'transferred_amount',
        'transfer_type_verbose', 'message'
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
            re.sub(',', '.', self.transferred_amount))
        if self.debcred == 'Af':
            self.transferred_amount = -self.transferred_amount
        try:
            self.execution_date = self.value_date = str2date(self.date,
                                                             '%Y%m%d')
        except ValueError:
            self.execution_date = self.value_date = str2date(self.date,
                                                             '%d-%m-%Y')
        self.statement_id = ''  # self.value_date.strftime('%Yw%W')
        self.id = str(subno).zfill(4)
        self.reference = ''
        # Normalize basic account numbers
        self.remote_account = self.remote_account.replace('.', '').zfill(10)
        self.local_account = self.local_account.replace('.', '').zfill(10)


class transaction(models.mem_bank_transaction):
    '''
    Implementation of transaction communication class for account_banking.
    '''
    attrnames = ['local_account', 'remote_account',
                 'remote_owner', 'transferred_amount',
                 'execution_date', 'value_date', 'transfer_type',
                 'id', 'reference', 'statement_id', 'message',
                 ]

    """
    Presumably the same transaction types occur in the MT940 format of ING.
    From www.ing.nl/Images/MT940_Technische_handleiding_tcm7-69020.pdf

    """
    type_map = {

        'AC': bt.ORDER,  # Acceptgiro
        'BA': bt.PAYMENT_TERMINAL,  # Betaalautomaattransactie
        'CH': bt.ORDER,  # Cheque
        'DV': bt.ORDER,  # Diversen
        'FL': bt.BANK_TERMINAL,  # Filiaalboeking, concernboeking
        'GF': bt.ORDER,  # Telefonisch bankieren
        'GM': bt.BANK_TERMINAL,  # Geldautomaat
        'GT': bt.ORDER,  # Internetbankieren
        'IC': bt.DIRECT_DEBIT,  # Incasso
        'OV': bt.ORDER,  # Overschrijving
        'PK': bt.BANK_TERMINAL,  # Opname kantoor
        'PO': bt.ORDER,  # Periodieke overschrijving
        'ST': bt.BANK_TERMINAL,  # Storting (eigen rekening of derde)
        'VZ': bt.ORDER,  # Verzamelbetaling
        'NO': bt.STORNO,  # Storno
        }

    # global expression for matching storno references
    ref_expr = re.compile('REF[\*:]([0-9A-Z-z_-]+)')
    # match references for Acceptgiro's through Internet banking
    kn_expr = re.compile('KN: ([^ ]+)')

    def __init__(self, line, *args, **kwargs):
        '''
        Initialize own dict with read values.
        '''
        super(transaction, self).__init__(*args, **kwargs)
        # Copy attributes from auxiliary class to self.
        for attr in self.attrnames:
            setattr(self, attr, getattr(line, attr))
        # self.message = ''
        # Decompose structured messages
        self.parse_message()
        # Adaptations to direct debit orders ands stornos
        if self.transfer_type == 'DV' and self.transferred_amount < 0:
            res = self.ref_expr.search(self.remote_owner)
            if res:
                self.transfer_type = 'NO'
                self.reference = res.group(1)
                self.remote_owner = False
            else:
                res = self.ref_expr.search(self.message)
                if res:
                    self.transfer_type = 'NO'
                    self.reference = res.group(1)
        if self.transfer_type == 'IC':
            if self.transferred_amount > 0:
                self.reference = self.remote_owner
            else:
                self.transfer_type = 'NO'
                self.message = self.remote_owner + self.message
                res = self.ref_expr.search(self.message)
                if res:
                    self.reference = res.group(1)
                    self.storno_retry = True
            self.remote_owner = False
        if self.transfer_type == 'GT':
            res = self.kn_expr.search(self.message)
            if res:
                self.reference = res.group(1)
        if self.transfer_type == 'AC':
            self.parse_acceptgiro()
        if self.message and not self.reference:
            self.reference = self.message

    def parse_acceptgiro(self):
        """
        Entries of type 'Acceptgiro' can contain the reference
        in the 'name' column, as well as full address information
        in the 'message' column'
        """
        before = False
        if self.remote_owner.startswith('KN: '):
            self.reference = self.remote_owner[4:]
            self.remote_owner = ''
        if 'KN: ' in self.message:
            index = self.message.index('KN: ')
            before = self.message[:index]
            self.message = self.message[index:]
        expression = (
            "^\s*(KN:\s*(?P<kn>[^\s]+))?(\s*)"
            "(?P<navr>NAVR:\s*[^\s]+)?(\s*)(?P<after>.*?)$")
        msg_match = re.match(expression, self.message)
        after = msg_match.group('after')
        kn = msg_match.group('kn')
        navr = msg_match.group('navr')
        if kn:
            self.reference = kn[4:]
        self.message = 'Acceptgiro %s' % (navr or '')
        if after:
            parts = [after[i:i+33] for i in range(0, len(after), 33)]
            if parts and not self.remote_owner:
                self.remote_owner = parts.pop(0).strip()
            if parts:
                self.remote_owner_address = [parts.pop(0).strip()]
            if parts:
                zip_city = parts.pop(0).strip()
                zip_match = re.match(
                    "^(?P<zipcode>[^ ]{6})\s+(?P<city>.*?)$", zip_city)
                if zip_match:
                    self.remote_owner_postalcode = zip_match.group('zipcode')
                    self.remote_owner_city = zip_match.group('city')
        if before and not self.remote_owner_city:
            self.remote_owner_city = before.strip()

    def is_valid(self):
        if not self.error_message:
            if not self.transferred_amount:
                self.error_message = "No transferred amount"
            elif not self.execution_date:
                self.error_message = "No execution date"
            elif not self.remote_account and self.transfer_type not in [
                    'BA', 'FL', 'GM', 'IC', 'PK', 'ST']:
                self.error_message = (
                    "No remote account for transaction type %s" %
                    self.transfer_type)
        return not self.error_message

    def parse_message(self):
        '''
        Parse structured message parts into appropriate attributes.
        No processing done here for Triodos, maybe later.
        '''


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
        try:
            self.date = str2date(msg.date, '%Y%m%d')
        except ValueError:
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
    code = 'ING'
    country_code = 'NL'
    name = _('ING Bank')
    doc = _('''\
The Dutch ING format is basicly a MS Excel CSV format. It is specifically
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
        statement_id = False
        for line in csv.reader(lines, dialect=dialect):
            # Skip empty (last) lines and header line
            if not line or line[0] == 'Datum':
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
