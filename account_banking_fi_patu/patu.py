# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 Sami Haahtinen (<http://ressukka.net>).
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
"""
This parser implements the PATU format support. PATU format is a generic format
used by finnish banks.
"""
from openerp.addons.account_banking.parsers import models
from openerp.tools.translate import _
from .parser import PatuParser

__all__ = ['Parser']


class Transaction(models.mem_bank_transaction):
    """Implementation of transaction communication class for account_banking.
    """
    mapping = {
        "remote_account": "recipientaccount",
        "remote_currency": "currency",
        "transferred_amount": "amount",
        "execution_date": "recorddate",
        "value_date": "paymentdate",
        "transfer_type": "eventtype",
        "reference": "refnr",
        "eventcode": "eventcode",
        "message": "message"
    }

    def __init__(self, record, *args, **kwargs):
        """Initialize own dict with read values."""
        super(Transaction, self).__init__(*args, **kwargs)
        for key in self.mapping:
            try:
                setattr(self, key, record[self.mapping[key]])
            except KeyError:
                pass

    def is_valid(self):
        """Override validity checks.
        There are certain situations for PATU which can be validated as
        invalid, but are normal.
        If eventcode is 730, the transaction was initiated by the bank and
        doesn't have a destination account.
        """
        if self.eventcode in ["720", "710"]:
            # Withdrawal from and deposit to the account
            return (self.execution_date and self.transferred_amount and True) \
                or False
        if self.eventcode and self.eventcode == "730":
            # The transaction is bank initiated, no remote account is present
            return (self.execution_date and self.transferred_amount and True) \
                or False
        return super(Transaction, self).is_valid()


class statement(models.mem_bank_statement):
    """Implementation of bank_statement communication class of account_banking
    """
    def __init__(self, record, *args, **kwargs):
        """
        Set decent start values based on first transaction read
        """
        super(statement, self).__init__(*args, **kwargs)
        self.id = record["statementnr"]
        self.local_account = self.convert_bank_account(record["accountnr"])
        self.date = record["creationdate"]
        self.start_balance = record["startingbalance"]

    def convert_bank_account(self, accountnr):
        """Convert bank account number in to a abbreviated format used in
        finland"""
        bank = accountnr[:6]
        account = accountnr[6:].lstrip("0")
        return "%s-%s" % (bank, account)

    def import_transaction(self, record):
        """Import a transaction to the statement"""
        if record["recordid"] == "40":
            self.end_balance = record["balance"]
        elif record["recordid"] == "10" or record["recordid"] == "80":
            # XXX: Sum up entries that have detailed records set for them. For
            # now, ignore the parent entry
            if record["receiptcode"] == "E":
                return
            self.transactions.append(Transaction(record))


class Parser(models.parser):
    code = 'FIPATU'
    name = _('PATU statement sheet')
    doc = _('''\
PATU statement format defines one or more statements in each file. This parser
will parse all statements in a file and import them to OpenERP
''')

    def parse(self, cr, data):
        result = []
        stmnt = None
        patuparser = PatuParser()
        for line in data.splitlines():
            # Skip empty (last) lines
            if not line:
                continue
            record = patuparser.parse_record(line)
            if record["recordid"] == "00":
                # New statement
                stmnt = statement(record)
                result.append(stmnt)
            else:
                stmnt.import_transaction(record)
        result.append(stmnt)
        return result
