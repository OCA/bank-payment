# -*- coding: utf-8 -*-
# © 2014-2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
"""
Parser for MT940 format files
"""

from __future__ import print_function
import re
import datetime
import logging
try:
    from openerp.addons.account_banking.parsers.models import (
        mem_bank_statement,
        mem_bank_transaction,
    )
    from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT
except ImportError:
    # this allows us to run this file standalone, see __main__ at the end

    class mem_bank_statement:
        def __init__(self):
            self.transactions = []

    class mem_bank_transaction:
        pass
    DEFAULT_SERVER_DATE_FORMAT = "%Y-%m-%d"


class MT940(object):
    """Inherit this class in your account_banking.parsers.models.parser,
    define functions to handle the tags you need to handle and adjust static
    variables as needed.

    Note that order matters: You need to do your_parser(MT940, parser), not the
    other way around!

    At least, you should override handle_tag_61 and handle_tag_86. Don't forget
    to call super.
    handle_tag_* functions receive the remainder of the the line (that is,
    without ':XX:') and are supposed to write into self.current_transaction"""

    header_lines = 3
    """One file can contain multiple statements, each with its own poorly
    documented header. For now, the best thing to do seems to skip that"""

    footer_regex = '^-}$'
    footer_regex = '^-XXX$'
    'The line that denotes end of message, we need to create a new statement'

    tag_regex = '^:[0-9]{2}[A-Z]*:'
    'The beginning of a record, should be anchored to beginning of the line'

    def __init__(self, *args, **kwargs):
        super(MT940, self).__init__(*args, **kwargs)
        self.current_statement = None
        'type account_banking.parsers.models.mem_bank_statement'
        self.current_transaction = None
        'type account_banking.parsers.models.mem_bank_transaction'
        self.statements = []
        'parsed statements up to now'

    def parse(self, cr, data):
        'implements account_banking.parsers.models.parser.parse()'
        iterator = data.replace('\r\n', '\n').split('\n').__iter__()
        line = None
        record_line = ''
        try:
            while True:
                if not self.current_statement:
                    self.handle_header(cr, line, iterator)
                line = iterator.next()
                if not self.is_tag(cr, line) and not self.is_footer(cr, line):
                    record_line = self.append_continuation_line(
                        cr, record_line, line)
                    continue
                if record_line:
                    self.handle_record(cr, record_line)
                if self.is_footer(cr, line):
                    self.handle_footer(cr, line, iterator)
                    record_line = ''
                    continue
                record_line = line
        except StopIteration:
            pass
        if self.current_statement:
            if record_line:
                self.handle_record(cr, record_line)
                record_line = ''
            self.statements.append(self.current_statement)
            self.current_statement = None
        return self.statements

    def append_continuation_line(self, cr, line, continuation_line):
        """append a continuation line for a multiline record.
        Override and do data cleanups as necessary."""
        return line + continuation_line

    def create_statement(self, cr):
        """create a mem_bank_statement - override if you need a custom
        implementation"""
        return mem_bank_statement()

    def create_transaction(self, cr):
        """create a mem_bank_transaction - override if you need a custom
        implementation"""
        return mem_bank_transaction()

    def is_footer(self, cr, line):
        """determine if a line is the footer of a statement"""
        return line and bool(re.match(self.footer_regex, line))

    def is_tag(self, cr, line):
        """determine if a line has a tag"""
        return line and bool(re.match(self.tag_regex, line))

    def handle_header(self, cr, line, iterator):
        """skip header lines, create current statement"""
        for i in range(self.header_lines):
            iterator.next()
        self.current_statement = self.create_statement(cr)

    def handle_footer(self, cr, line, iterator):
        """add current statement to list, reset state"""
        self.statements.append(self.current_statement)
        self.current_statement = None

    def handle_record(self, cr, line):
        """find a function to handle the record represented by line"""
        tag_match = re.match(self.tag_regex, line)
        tag = tag_match.group(0).strip(':')
        if not hasattr(self, 'handle_tag_%s' % tag):
            logging.error('Unknown tag %s', tag)
            logging.error(line)
            return
        handler = getattr(self, 'handle_tag_%s' % tag)
        handler(cr, line[tag_match.end():])

    def handle_tag_20(self, cr, data):
        """ignore reference number"""
        pass

    def handle_tag_25(self, cr, data):
        """get account owner information"""
        self.current_statement.local_account = data

    def handle_tag_28C(self, cr, data):
        """get sequence number _within_this_batch_ - this alone
        doesn't provide a unique id!"""
        self.current_statement.id = data

    def handle_tag_60F(self, cr, data):
        """get start balance and currency"""
        self.current_statement.local_currency = data[7:10]
        self.current_statement.date = str2date(data[1:7])
        self.current_statement.start_balance = \
            (1 if data[0] == 'C' else -1) * str2float(data[10:])
        self.current_statement.id = '%s/%s' % (
            self.current_statement.date.strftime('%Y'),
            self.current_statement.id)

    def handle_tag_62F(self, cr, data):
        """get ending balance"""
        self.current_statement.end_balance = \
            (1 if data[0] == 'C' else -1) * str2float(data[10:])

    def handle_tag_64(self, cr, data):
        """get current balance in currency"""
        pass

    def handle_tag_65(self, cr, data):
        """get future balance in currency"""
        pass

    def handle_tag_61(self, cr, data):
        """get transaction values"""
        transaction = self.create_transaction(cr)
        self.current_statement.transactions.append(transaction)
        self.current_transaction = transaction
        transaction.execution_date = str2date(data[:6])
        transaction.effective_date = str2date(data[:6])
        transaction.value_date = str2date(data[:6])
        #  ...and the rest already is highly bank dependent

    def handle_tag_86(self, cr, data):
        """details for previous transaction, here most differences between
        banks occur"""
        pass


def str2date(string, fmt='%y%m%d'):
    return datetime.datetime.strptime(string, fmt)


def str2float(string):
    return float(string.replace(',', '.'))


def main(filename):
    """testing"""
    parser = MT940()
    parser.parse(None, open(filename, 'r').read())
    for statement in parser.statements:
        print(
            "statement found for %(local_account)s at %(date)s"
            " with %(local_currency)s%(start_balance)s to %(end_balance)s" %
            statement.__dict__
        )
        for transaction in statement.transactions:
            print(
                "transaction on %(execution_date)s" % transaction.__dict__
            )


if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
