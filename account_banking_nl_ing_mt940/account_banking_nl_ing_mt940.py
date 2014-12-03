# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
import re
from openerp.tools.translate import _
from openerp.addons.account_banking.parsers.models import (
    parser,
    mem_bank_transaction,
)
from openerp.addons.account_banking_mt940.mt940 import MT940, str2float


class transaction(mem_bank_transaction):
    def is_valid(self):
        '''allow transactions without remote account'''
        return bool(self.execution_date) and bool(self.transferred_amount)


class IngMT940Parser(MT940, parser):
    name = _('ING MT940 (structured)')
    country_code = 'NL'
    code = 'INT_MT940_STRUC'

    tag_61_regex = re.compile(
        r'^(?P<date>\d{6})(?P<sign>[CD])(?P<amount>\d+,\d{2})N(?P<type>.{3})'
        r'(?P<reference>\w{1,16})')

    def create_transaction(self, cr):
        return transaction()

    def handle_tag_25(self, cr, data):
        '''ING: For current accounts: IBAN+ ISO 4217 currency code'''
        self.current_statement.local_account = data[:-3]

    def handle_tag_60F(self, cr, data):
        super(IngMT940Parser, self).handle_tag_60F(cr, data)
        self.current_statement.id = '%s-%s' % (
            self.get_unique_account_identifier(
                cr, self.current_statement.local_account),
            self.current_statement.id)

    def handle_tag_61(self, cr, data):
        super(IngMT940Parser, self).handle_tag_61(cr, data)
        parsed_data = self.tag_61_regex.match(data).groupdict()
        self.current_transaction.transferred_amount = \
            (-1 if parsed_data['sign'] == 'D' else 1) * str2float(
                parsed_data['amount'])
        self.current_transaction.reference = parsed_data['reference']

    def handle_tag_86(self, cr, data):
        if not self.current_transaction:
            return
        super(IngMT940Parser, self).handle_tag_86(cr, data)
        codewords = ['RTRN', 'BENM', 'ORDP', 'CSID', 'BUSP', 'MARF', 'EREF',
                     'PREF', 'REMI', 'ID', 'PURP', 'ULTB', 'ULTD',
                     'CREF', 'IREF', 'CNTP', 'ULTC', 'EXCH', 'CHGS']
        subfields = {}
        current_codeword = None
        for word in data.split('/'):
            if not word and not current_codeword:
                continue
            if word in codewords:
                current_codeword = word
                subfields[current_codeword] = []
                continue
            if current_codeword in subfields:
                subfields[current_codeword].append(word)

        if 'CNTP' in subfields:
            self.current_transaction.remote_account = subfields['CNTP'][0]
            self.current_transaction.remote_bank_bic = subfields['CNTP'][1]
            self.current_transaction.remote_owner = subfields['CNTP'][2]
            self.current_transaction.remote_owner_city = subfields['CNTP'][3]

        if 'BENM' in subfields:
            self.current_transaction.remote_account = subfields['BENM'][0]
            self.current_transaction.remote_bank_bic = subfields['BENM'][1]
            self.current_transaction.remote_owner = subfields['BENM'][2]
            self.current_transaction.remote_owner_city = subfields['BENM'][3]

        if 'ORDP' in subfields:
            self.current_transaction.remote_account = subfields['ORDP'][0]
            self.current_transaction.remote_bank_bic = subfields['ORDP'][1]
            self.current_transaction.remote_owner = subfields['ORDP'][2]
            self.current_transaction.remote_owner_city = subfields['ORDP'][3]

        if 'REMI' in subfields:
            self.current_transaction.message = '/'.join(
                filter(lambda x: bool(x), subfields['REMI']))

        if self.current_transaction.reference in subfields:
            self.current_transaction.reference = ''.join(
                subfields[self.current_transaction.reference])

        if not subfields:
            self.current_transaction.message = data

        self.current_transaction = None
