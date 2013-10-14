# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 credativ Ltd (<http://www.credativ.co.uk>).
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
# Imports LLoyds Corporate format
#

from account_banking.parsers import models, convert
from tools.translate import _
import re
import osv
import logging
import csv
from StringIO import StringIO
from operator import itemgetter

logger = logging.getLogger('lloydscorporate_csv_import')

class CSVTransaction(models.mem_bank_transaction):

    mapping = {
        'execution_date' : 'date',
        'effective_date': 'date',
        'message' : 'description',
        'name' : 'description',          # Use description as transaction name
        'balance' : 'Balance',           # Store balance from line for calculating statement balances
    }

    def __init__(self, record, *args, **kwargs):
        '''
        Transaction creation
        '''
        super(CSVTransaction, self).__init__(*args, **kwargs)

        # Parse date of format 01APR13
        record['date'] = convert.str2date(re.sub(r'\W*','',record['Date']), '%d%b%y')

        record['description'] = record['Narrative'].strip()

        # Mapping of simple items
        for key, value in self.mapping.iteritems():
            if record.has_key(value):
                setattr(self, key, record[value])

        # Convert debit/credit to float amount
        if len(record['Payments'].strip()):
            self.transferred_amount = record['Payments'] and -float(record['Payments']) or 0.0
        else:
            self.transferred_amount = record['Receipts'] and float(record['Receipts']) or 0.0

        # Cheque - set reference
        transfer_account = re.match(r'\w*\s\d{1,12}$', record['description'])
        if transfer_account:
            self.reference = transfer_account.group()

        if not self.is_valid():
            logger.info("Invalid: %s", record)

    def is_valid(self):
        '''
        We don't have remote_account so override base
        '''
        return (self.execution_date
                and self.transferred_amount and True) or False

class Statement(models.mem_bank_statement):

    def import_statement(self, record):
        self.transactions.append(CSVTransaction(record))

def raise_error(message, line):
    raise osv.osv.except_osv(_('Import error'),
        'Error in import:%s\n\n%s' % (message, line))

class parser(models.parser):
    code = 'LLOYDSCORPORATE-CSV'
    name = _('Lloyds Corporate CSV Statement IMPORT')
    country_code = 'GB'
    doc = _('''\
            This format is available through
            the web interface.
            ''')

    def parse(self, cr, data):
        ''' Lloyds corporate CSV parser'''

        data = data.replace('\r','')
        csv_header = data.split('\n')[0].replace('"', '').split(',')
        header_list = ['Account', 'Date', 'Type', 'Narrative', 'Value Date', 'Payments', 'Receipts', 'Balance']
        result = []

        #compare header list and process csv if equal
        if cmp(csv_header,header_list) != 0:
            logger.info("Invalid import Statement:")
            logger.info("Expected Header: %s" %(str(header_list)))
            logger.info("Header found: %s"%(str(csv_header)))
            raise osv.osv.except_osv(_('Import error'),
                'Error in import:%s\n' % (_('Invalid file format')))

        bankdata = StringIO(data)
        lines = list(csv.DictReader(bankdata))
        stmnt = Statement()
        # lines as they are imported
        if len(lines):
            #Store opening balance from first record
            line = lines[0]
            stmnt.start_balance = line['Balance']
            account_number = re.sub('\D', '', line['Account'])

            #Assuming if payment and receipts are both null then its opening balance
            if not (line['Payments'] and line['Receipts']):
                lines = lines[1:]

            #Skip records which do not contains transaction type
            for line in lines[:-int(len(lines)-map(itemgetter('Type'), lines).index(''))]:
                #create Statement lines from csv records
                stmnt.import_statement(line)

            #Get statement Closing balance from CSV data list
            try:
                stmnt.end_balance = lines[map(itemgetter('Narrative'), lines).\
                                  index('Closing Ledger Balance')]['Balance']
            except ValueError:
                raise osv.osv.except_osv(_('Closing Balance'),
                        _('Statement Closing Balance not found.'))


            #GB account number format stored in ERP
            stmnt.local_account = account_number[:6] +' '+ account_number[6:]

            # Take date of last line of statement
            stmnt.date = stmnt.transactions[-1].effective_date

        statement_id = self.get_unique_statement_id(
            cr, stmnt.date.strftime('%Yw%W'))
        stmnt.id = statement_id
        result.append(stmnt)
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
