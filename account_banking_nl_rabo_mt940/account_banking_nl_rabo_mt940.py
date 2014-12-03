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
from openerp.addons.account_banking.parsers.models import parser,\
    mem_bank_transaction
from openerp.addons.account_banking_mt940.mt940 import MT940, str2float


class transaction(mem_bank_transaction):
    def is_valid(self):
        '''allow transactions without remote account'''
        return bool(self.execution_date) and bool(self.transferred_amount)


class RaboMT940Parser(MT940, parser):
    name = _('MT940 Rabobank structured')
    country_code = 'NL'
    code = 'MT940 Rabobank'
    header_lines = 1

    tag_61_regex = re.compile(
        r'^(?P<date>\d{6})(?P<sign>[CD])(?P<amount>\d+,\d{2})N(?P<type>.{3})'
        r'(?P<reference>\w{1,16})')

    def parse(self, cr, data):
        'implements account_banking.parsers.models.parser.parse()'
        res = super(RaboMT940Parser, self).parse(cr, data + '\n-XXX')
        return res

    def handle_tag_25(self, cr, data):
        '''get account owner information'''
        self.current_statement.local_account = data.split(' ')[0]

    def create_transaction(self, cr):
        return transaction()

    def handle_tag_60F(self, cr, data):
        super(RaboMT940Parser, self).handle_tag_60F(cr, data)
        self.current_statement.id = '%s-%s' % (
            self.get_unique_account_identifier(
                cr, self.current_statement.local_account),
            self.current_statement.id)

    def handle_tag_61(self, cr, data):
        super(RaboMT940Parser, self).handle_tag_61(cr, data)
        parsed_data = self.tag_61_regex.match(data).groupdict()
        self.current_transaction.transferred_amount = \
            (-1 if parsed_data['sign'] == 'D' else 1) * str2float(
                parsed_data['amount'])
        reference = parsed_data['reference']
        self.current_transaction.reference = reference
        # Bank account is last field, following reference. In some cases
        # there might be a reference of the other bank. In that case the
        # reference will be followed by '//' and the 16 positions for the
        # other bank;
        account_start = data.find(reference)
        if account_start >= 0:
            # If no reference found, we can not determine bank-account.
            account_start += len(reference)
            # check for other bank
            other_start = data.find('//')
            if other_start >= 0:
                account_start = other_start + 18
            if account_start < len(data):
                self.current_transaction.remote_account = (
                    data[account_start:].strip())

    def handle_tag_86(self, cr, data):
        if not self.current_transaction:
            return
        super(RaboMT940Parser, self).handle_tag_86(cr, data)
        codewords = ['MARF', 'EREF', 'PREF', 'RTRN', 'ACCW', 'BENM',
                     'ORDP', 'NAME', 'ID', 'ADDR', 'REMI', 'CDTRREFTP',
                     'CD', 'SCOR', 'ISSR', 'CUR', 'CDTRREF', 'CSID', 'ISDT',
                     'ULTD', 'ULTB', 'PURP']
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

        if 'NAME' in subfields:
            self.current_transaction.remote_owner = (
                ' '.join(subfields['NAME']))

        if 'ADDR' in subfields:
            # Do NOT join address fields, array is expected on other code!
            self.current_transaction.remote_owner_address = subfields['ADDR']

        if 'REMI' in subfields:
            self.current_transaction.message = '/'.join(
                f for f in subfields['REMI'] if f)

        if self.current_transaction.reference in subfields:
            self.current_transaction.reference = ''.join(
                subfields[self.current_transaction.reference])

        if not subfields:
            self.current_transaction.message = data

        self.current_transaction = None
