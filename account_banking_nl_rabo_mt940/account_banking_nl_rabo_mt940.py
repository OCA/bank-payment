# -*- coding: utf-8 -*-
"""Implement parser for MT940 files - Rabobank dialect."""
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Therp BV <http://therp.nl>.
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
from string import printable
import logging
from datetime import datetime
from openerp.tools.translate import _
from openerp.addons.account_banking.parsers.models import (
    parser,
    mem_bank_transaction,
)
from openerp.addons.account_banking_mt940.mt940 import MT940, str2float


class RabobankTransaction(mem_bank_transaction):
    """Extentions for MT940 Rabobank transactions."""

    def is_valid(self):
        """allow transactions without remote account"""
        if bool(self.execution_date) and bool(self.transferred_amount):
            return True
        if not bool(self.execution_date):
            logging.debug(_('Missing execution_date in transaction'))
        if not bool(self.transferred_amount):
            logging.debug(_('Missing transferred_amount in transaction'))
        return False


class RaboMT940Parser(MT940, parser):
    """Implement parser for MT940 files - Rabobank dialect."""
    name = _('MT940 Rabobank structured')
    country_code = 'NL'
    code = 'MT940 Rabobank'
    header_lines = 1

    tag_61_regex = re.compile(
        r'^(?P<date>\d{6})(?P<sign>[CD])(?P<amount>\d+,\d{2})N(?P<type>.{3})'
        r'(?P<reference>\w{1,16})')

    def parse(self, cr, data):
        """Filter Unprintable characters from file data.

        The file contents of the Rabobank tend to contain unprintable
        characters that prevent proper parsing. These will be removed.
        """
        data = ''.join([x for x in data if x in printable])
        return super(RaboMT940Parser, self).parse(cr, data)

    def create_transaction(self, cr):
        """Return Rabobank Transaction (with overriden is_valid() method)."""
        return RabobankTransaction()

    def handle_tag_25(self, cr, data):
        """Handle tag 25: local bank account information."""
        data = data.replace('EUR', '').replace('.', '').strip()
        super(RaboMT940Parser, self).handle_tag_25(cr, data)

    def handle_tag_60F(self, cr, data):
        """get start balance and currency"""
        # For the moment only first 60F record
        # The alternative would be to split the file and start a new
        # statement for each 20: tag encountered.
        stmt = self.current_statement
        if not stmt.local_currency:
            stmt.local_currency = data[7:10]
            stmt.date = datetime.strptime(data[1:7], '%y%m%d')
            stmt.start_balance = (
                (1 if data[0] == 'C' else -1) * str2float(data[10:]))
            stmt.id = '%s-%s' % (
                self.get_unique_account_identifier(cr, stmt.local_account),
                stmt.id)

    def handle_tag_61(self, cr, data):
        """Handle tag 61: transaction data."""
        super(RaboMT940Parser, self).handle_tag_61(cr, data)
        parsed_data = self.tag_61_regex.match(data).groupdict()
        self.current_transaction.transferred_amount = \
            (-1 if parsed_data['sign'] == 'D' else 1) * str2float(
                parsed_data['amount'])
        self.current_transaction.reference = parsed_data['reference']

    def handle_tag_86(self, cr, data):
        """Handle tag 86: transaction details"""
        if not self.current_transaction:
            return

        def get_counterpart(transaction, subfield):
            """Same information can come from different field."""
            if not subfield:
                return  # subfield is empty
            if len(subfield) >= 1 and subfield[0]:
                transaction.remote_account = subfield[0]
            if len(subfield) >= 2 and subfield[1]:
                transaction.remote_bank_bic = subfield[1]
            if len(subfield) >= 3 and subfield[2]:
                transaction.remote_owner = subfield[2]
            if len(subfield) >= 4 and subfield[3]:
                transaction.remote_owner_city = subfield[3]

        super(RaboMT940Parser, self).handle_tag_86(cr, data)
        codewords = ['RTRN', 'BENM', 'ORDP', 'CSID', 'BUSP', 'MARF', 'EREF',
                     'PREF', 'REMI', 'ID', 'PURP', 'ULTB', 'ULTD',
                     'CREF', 'IREF', 'NAME', 'ADDR', 'ULTC', 'EXCH', 'CHGS']
        # Fill subfields:
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
        # Use subfields for transaction details:
        if 'NAME' in subfields:
            self.current_transaction.remote_owner = (
                ' '.join(subfields['NAME']))
        if 'ADDR' in subfields:
            # Do NOT join address fields, array is expected on other code!
            self.current_transaction.remote_owner_address = subfields['ADDR']
        if 'BENM' in subfields:
            get_counterpart(self.current_transaction, subfields['BENM'])
        if 'ORDP' in subfields:
            get_counterpart(self.current_transaction, subfields['ORDP'])
        if 'REMI' in subfields:
            self.current_transaction.message = '/'.join(
                f for f in subfields['REMI'] if f)
        if self.current_transaction.reference in subfields:
            self.current_transaction.reference = ''.join(
                subfields[self.current_transaction.reference])
        if not subfields:
            self.current_transaction.message = data
        self.current_transaction = None

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
