# -*- coding: utf-8 -*-
"""Define mt940 parser for Dutch ING bank."""
##############################################################################
#
#    Copyright (C) 2014-2015 Therp BV <http://therp.nl>.
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
from openerp.addons.account_banking_mt940.mt940 import (
    MT940, str2amount, get_subfields, handle_common_subfields)


class IngMT940Parser(MT940):
    """Define mt940 parser for Dutch ING bank."""
    name = _('ING MT940 (structured)')
    country_code = 'NL'
    code = 'INT_MT940_STRUC'

    tag_61_regex = re.compile(
        r'^(?P<date>\d{6})(?P<line_date>\d{0,4})'
        r'(?P<sign>[CD])(?P<amount>\d+,\d{2})N(?P<type>.{3})'
        r'(?P<reference>\w{1,50})'
    )

    def handle_tag_61(self, data):
        """Parse 61 tag containing transaction data."""
        super(IngMT940Parser, self).handle_tag_61(data)
        re_61 = self.tag_61_regex.match(data)
        if not re_61:
            raise ValueError("Cannot parse %s" % data)
        parsed_data = re_61.groupdict()
        self.current_transaction.transferred_amount = (
            str2amount(parsed_data['sign'], parsed_data['amount']))
        self.current_transaction.reference = parsed_data['reference']

    def handle_tag_86(self, data):
        """Parse 86 tag containing reference data."""
        if not self.current_transaction:
            return
        codewords = ['RTRN', 'BENM', 'ORDP', 'CSID', 'BUSP', 'MARF', 'EREF',
                     'PREF', 'REMI', 'ID', 'PURP', 'ULTB', 'ULTD',
                     'CREF', 'IREF', 'CNTP', 'ULTC', 'EXCH', 'CHGS']
        subfields = get_subfields(data, codewords)
        transaction = self.current_transaction
        # If we have no subfields, set message to whole of data passed:
        if not subfields:
            transaction.message = data
        else:
            handle_common_subfields(transaction, subfields)
        # Prevent handling tag 86 later for non transaction details:
        self.current_transaction = None
