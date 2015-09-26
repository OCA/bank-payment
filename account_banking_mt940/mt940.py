#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Parser for MT940 format files."""
##############################################################################
#
#    OpenERP, Open Source Management Solution
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
from __future__ import print_function
import re
from datetime import datetime
import logging
try:
    from openerp.tools.translate import _
    from openerp.addons.account_banking.parsers.models import (
        mem_bank_statement,
        mem_bank_transaction,
        parser
    )
except ImportError:
    # this allows us to run this file standalone, see __main__ at the end
    class mem_bank_statement(object):
        """Dummy class"""
        def __init__(self):
            """Just define transactions array."""
            self.transactions = []
            self.local_currency = ''
            self.local_account = ''

    class mem_bank_transaction(object):
        """Dummy class"""
        pass

    class parser(object):
        """Dummy class"""
        def parse(self, cr, data):
            """Dummy method, so super can be called."""
            pass


def str2amount(sign, str_amount):
    """Convert sign (C or D) and amount in string to signed amount (float)."""
    factor = (1 if sign == 'C' else -1)
    return factor * float(str_amount.replace(',', '.'))


def get_subfields(data, codewords):
    """Return dictionary with value array for each codeword in data.

    For instance:
    data =
        /BENM//NAME/Kosten/REMI/Periode 01-10-2013 t/m 31-12-2013/ISDT/20
    codewords = ['BENM', 'ADDR', 'NAME', 'CNTP', ISDT', 'REMI']
    Then return subfields = {
        'BENM': [],
        'NAME': ['Kosten'],
        'REMI': ['Periode 01-10-2013 t', 'm 31-12-2013'],
        'ISDT': ['20'],
    }
    """
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
    return subfields


def get_counterpart(transaction, subfield):
    """Get counterpart from transaction.

    Counterpart is often stored in subfield of tag 86. The subfield
    can be BENM, ORDP, CNTP"""
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


def handle_common_subfields(transaction, subfields):
    """Deal with common functionality for tag 86 subfields."""
    # Get counterpart from CNTP, BENM or ORDP subfields:
    for counterpart_field in ['CNTP', 'BENM', 'ORDP']:
        if counterpart_field in subfields:
            get_counterpart(transaction, subfields[counterpart_field])
    # REMI: Remitter information (text entered by other party on trans.):
    if 'REMI' in subfields:
        transaction.message = (
            '/'.join(x for x in subfields['REMI'] if x))
    # Get transaction reference subfield (might vary):
    if transaction.reference in subfields:
        transaction.reference = ''.join(
            subfields[transaction.reference])


class MT940Transaction(mem_bank_transaction):
    """Extentions for MT940 transactions."""

    def is_valid(self):
        """allow transactions without remote account"""
        if bool(self.execution_date) and bool(self.transferred_amount):
            return True
        if not bool(self.execution_date):
            logging.debug(_('Missing execution_date in transaction'))
        if not bool(self.transferred_amount):
            logging.debug(_('Missing transferred_amount in transaction'))
        return False


class MT940(parser):
    """Inherit this class in your account_banking.parsers.models.parser,
    define functions to handle the tags you need to handle and adjust static
    variables as needed.

    At least, you should override handle_tag_61 and handle_tag_86. Don't forget
    to call super.

    handle_tag_* functions receive the remainder of the the line (that is,
    without ':XX:') and are supposed to write into self.current_transaction
    """

    def __init__(self, *args, **kwargs):
        """Initialize parser - override at least header_regex.

        This in fact uses the ING syntax, override in others.
        """
        self.header_lines = 3  # Number of lines to skip
        # (old) Ing or Rabobank header:
        self.header_regex = '^0000 01INGBNL2AXXXX|^{1|^:940'
        self.footer_regex = '^-}$|^-XXX$'  # Stop processing on seeing this
        self.tag_regex = '^:[0-9]{2}[A-Z]*:'  # Start of new tag
        super(MT940, self).__init__(*args, **kwargs)
        self.current_statement = None
        self.current_transaction = None
        self.statements = []

    def is_mt940(self, data):
        """determine if a line is the header of a statement"""
        if not bool(re.match(self.header_regex, data)):
            raise ValueError(
                'File starting with %s does not seem to be a'
                ' MT940 format bank statement.' %
                data[:12]
            )

    def parse(self, cr, data):
        """Implements account_banking.parsers.models.parser.parse()."""
        self.is_mt940(data)
        iterator = data.replace('\r\n', '\n').split('\n').__iter__()
        line = None
        record_line = ''
        try:
            while True:
                if not self.current_statement:
                    self.handle_header(line, iterator)
                line = iterator.next()
                if not self.is_tag(line) and not self.is_footer(line):
                    record_line = self.append_continuation_line(
                        record_line, line)
                    continue
                if record_line:
                    self.handle_record(record_line)
                if self.is_footer(line):
                    self.handle_footer(line, iterator)
                    record_line = ''
                    continue
                record_line = line
        except StopIteration:
            pass
        if self.current_statement:
            if record_line:
                self.handle_record(record_line)
                record_line = ''
            self.statements.append(self.current_statement)
            self.current_statement = None
        return self.statements

    def append_continuation_line(self, line, continuation_line):
        """append a continuation line for a multiline record.
        Override and do data cleanups as necessary."""
        return line + continuation_line

    def create_statement(self):
        """Create a mem_bank_statement."""
        return mem_bank_statement()

    def create_transaction(self):
        """Override to return MT940 transaction."""
        return MT940Transaction()

    def is_footer(self, line):
        """determine if a line is the footer of a statement"""
        return line and bool(re.match(self.footer_regex, line))

    def is_tag(self, line):
        """determine if a line has a tag"""
        return line and bool(re.match(self.tag_regex, line))

    def handle_header(self, dummy_line, iterator):
        """skip header lines, create current statement"""
        for dummy_i in range(self.header_lines):
            iterator.next()
        self.current_statement = self.create_statement()

    def handle_footer(self, dummy_line, dummy_iterator):
        """add current statement to list, reset state"""
        self.statements.append(self.current_statement)
        self.current_statement = None

    def handle_record(self, line):
        """find a function to handle the record represented by line"""
        tag_match = re.match(self.tag_regex, line)
        tag = tag_match.group(0).strip(':')
        if not hasattr(self, 'handle_tag_%s' % tag):
            logging.error('Unknown tag %s', tag)
            logging.error(line)
            return
        handler = getattr(self, 'handle_tag_%s' % tag)
        handler(line[tag_match.end():])

    def handle_tag_20(self, data):
        """ignore reference number"""
        pass

    def handle_tag_25(self, data):
        """Handle tag 25: local bank account information."""
        data = data.replace('EUR', '').replace('.', '').strip()
        self.current_statement.local_account = data

    def handle_tag_28C(self, data):
        """Sequence number within batch - normally only zeroes."""
        pass

    def handle_tag_60F(self, data):
        """get start balance and currency"""
        # For the moment only first 60F record
        # The alternative would be to split the file and start a new
        # statement for each 20: tag encountered.
        stmt = self.current_statement
        if not stmt.local_currency:
            stmt.local_currency = data[7:10]
            stmt.start_balance = str2amount(data[0], data[10:])

    def handle_tag_61(self, data):
        """get transaction values"""
        transaction = self.create_transaction()
        self.current_statement.transactions.append(transaction)
        self.current_transaction = transaction
        transaction.execution_date = datetime.strptime(data[:6], '%y%m%d')
        transaction.value_date = datetime.strptime(data[:6], '%y%m%d')
        #  ...and the rest already is highly bank dependent

    def handle_tag_62F(self, data):
        """Get ending balance, statement date and id.

        We use the date on the last 62F tag as statement date, as the date
        on the 60F record (previous end balance) might contain a date in
        a previous period.

        We generate the statement.id from the local_account and the end-date,
        this should normally be unique, provided there is a maximum of
        one statement per day.

        Depending on the bank, there might be multiple 62F tags in the import
        file. The last one counts.
        """
        stmt = self.current_statement
        stmt.end_balance = str2amount(data[0], data[10:])
        stmt.date = datetime.strptime(data[1:7], '%y%m%d')
        stmt.id = '%s-%s' % (
            stmt.local_account,
            stmt.date.strftime('%Y-%m-%d'),
        )

    def handle_tag_64(self, data):
        """get current balance in currency"""
        pass

    def handle_tag_65(self, data):
        """get future balance in currency"""
        pass

    def handle_tag_86(self, data):
        """details for previous transaction, here most differences between
        banks occur"""
        pass


def main(filename):
    """testing"""
    parser_obj = MT940()
    parser_obj.parse(None, open(filename, 'r').read())
    for statement in parser_obj.statements:
        print(
            "statement found for %(local_account)s at %(date)s"
            " with %(local_currency)s%(start_balance)s to %(end_balance)s" %
            statement.__dict__
        )
        for transaction in statement.transactions:
            print(
                "transaction on %(execution_date)s" % transaction.__dict__)

if __name__ == '__main__':
    import sys
    main(sys.argv[1])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
