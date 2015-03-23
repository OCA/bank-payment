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
from datetime import datetime
from openerp.tools.translate import _
from openerp.addons.account_banking_mt940.mt940 import (
    MT940, str2float, get_subfields, handle_common_subfields)


class RaboMT940Parser(MT940):
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

    def handle_tag_60F(self, data):
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
                self.current_statement.date.strftime('%Y-%m-%d'),
                self.current_statement.id)

    def handle_tag_61(self, data):
        """Handle tag 61: transaction data."""
        super(RaboMT940Parser, self).handle_tag_61(data)
        parsed_data = self.tag_61_regex.match(data).groupdict()
        self.current_transaction.transferred_amount = \
            (-1 if parsed_data['sign'] == 'D' else 1) * str2float(
                parsed_data['amount'])
        self.current_transaction.reference = parsed_data['reference']

    def handle_tag_86(self, data):
        """Handle tag 86: transaction details"""
        if not self.current_transaction:
            return
        codewords = ['RTRN', 'BENM', 'ORDP', 'CSID', 'BUSP', 'MARF', 'EREF',
                     'PREF', 'REMI', 'ID', 'PURP', 'ULTB', 'ULTD',
                     'CREF', 'IREF', 'NAME', 'ADDR', 'ULTC', 'EXCH', 'CHGS']
        subfields = get_subfields(data, codewords)
        transaction = self.current_transaction
        # If we have no subfields, set message to whole of data passed:
        if not subfields:
            transaction.message = data
        else:
            handle_common_subfields(transaction, subfields)
            # Use subfields for transaction details:
            if 'NAME' in subfields:
                transaction.remote_owner = ' '.join(subfields['NAME'])
            if 'ADDR' in subfields:
                # Do NOT join address fields, array is expected on other code!
                transaction.remote_owner_address = subfields['ADDR']
        # Prevent handling tag 86 later for non transaction details:
        self.current_transaction = None

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
