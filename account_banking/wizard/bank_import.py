# -*- coding: utf-8 -*-
##############################################################################
#
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
# Many thanks to our contributors
#
# Kaspars Vilkens (KNdati): lenghty discussions, bugreports and bugfixes
# Stefan Rijnhart (Therp): bugreport and bugfix
#

'''
This module contains the business logic of the wizard account_banking_import.
The parsing is done in the parser modules. Every parser module is required to
use parser.models as a mean of communication with the business logic.
'''
import base64
import datetime
from StringIO import StringIO
from zipfile import ZipFile, BadZipfile  # BadZipFile in Python >= 3.2

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.decimal_precision import decimal_precision as dp

from ..parsers import models
from ..parsers import convert
from ..struct import struct
from . import banktools

bt = models.mem_bank_transaction

# This variable is used to match supplier invoices with an invoice date after
# the real payment date. This can occur with online transactions (web shops).
payment_window = datetime.timedelta(days=10)


def parser_types(*args, **kwargs):
    '''Delay evaluation of parser types until start of wizard, to allow
       depending modules to initialize and add their parsers to the list
    '''
    return models.parser_type.get_parser_types()


class banking_import_line(orm.TransientModel):
    _name = 'banking.import.line'
    _description = 'Bank import lines'
    _columns = {
        'name': fields.char('Name', size=64),
        'date': fields.date('Date', readonly=True),
        'amount': fields.float(
            'Amount',
            digits_compute=dp.get_precision('Account'),
        ),
        'statement_line_id': fields.many2one(
            'account.bank.statement.line',
            'Resulting statement line', readonly=True),
        'type': fields.selection(
            [
                ('supplier', 'Supplier'),
                ('customer', 'Customer'),
                ('general', 'General')
            ],
            'Type', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'statement_id': fields.many2one(
            'account.bank.statement',
            'Statement',
            select=True,
            required=True,
            ondelete='cascade',
        ),
        'ref': fields.char('Reference', size=32),
        'note': fields.text('Notes'),
        'period_id': fields.many2one('account.period', 'Period'),
        'currency': fields.many2one('res.currency', 'Currency'),
        'banking_import_id': fields.many2one(
            'account.banking.bank.import', 'Bank import',
            readonly=True, ondelete='cascade'),
        'reconcile_id': fields.many2one(
            'account.move.reconcile', 'Reconciliaton'),
        'account_id': fields.many2one('account.account', 'Account'),
        'invoice_ids': fields.many2many(
            'account.invoice', 'banking_import_line_invoice_rel',
            'line_id', 'invoice_id'),
        'partner_bank_id': fields.many2one('res.partner.bank', 'Bank Account'),
        'transaction_type': fields.selection(
            [
                # TODO: payment terminal etc...
                ('invoice', 'Invoice payment'),
                ('storno', 'Canceled debit order'),
                ('bank_costs', 'Bank costs'),
                ('unknown', 'Unknown'),
            ],
            'Transaction type',
        ),
        'duplicate': fields.boolean('Duplicate'),
    }


class banking_import(orm.TransientModel):
    _name = 'account.banking.bank.import'

    def import_statements_file(self, cr, uid, ids, context):
        '''
        Import bank statements / bank transactions file.
        This method is a wrapper for the business logic on the transaction.
        The parser modules represent the decoding logic.
        '''
        banking_import = self.browse(cr, uid, ids, context)[0]
        statements_file = banking_import.file
        data = base64.decodestring(statements_file)
        files = [data]
        try:
            with ZipFile(StringIO(data), 'r') as archive:
                files = [
                    archive.read(filename) for filename in archive.namelist()
                    if not filename.endswith('/')
                    ]
        except BadZipfile:
            pass

        user_obj = self.pool.get('res.user')
        statement_obj = self.pool.get('account.bank.statement')
        statement_file_obj = self.pool.get('account.banking.imported.file')
        import_transaction_obj = self.pool.get('banking.import.transaction')
        period_obj = self.pool.get('account.period')

        # get the parser to parse the file
        parser_code = banking_import.parser
        parser = models.create_parser(parser_code)
        if not parser:
            raise orm.except_orm(
                _('ERROR!'),
                _('Unable to import parser %(parser)s. Parser class not '
                  'found.') %
                {'parser': parser_code}
            )

        # Get the company
        company = (banking_import.company or
                   user_obj.browse(cr, uid, uid, context).company_id)

        # Parse the file(s)
        statements = []
        for import_file in files:
            statements += parser.parse(cr, import_file)

        if any([x for x in statements if not x.is_valid()]):
            raise orm.except_orm(
                _('ERROR!'),
                _('The imported statements appear to be invalid! Check your '
                  'file.')
            )

        # Create the file now, as the statements need to be linked to it
        import_id = statement_file_obj.create(cr, uid, dict(
            company_id=company.id,
            file=statements_file,
            file_name=banking_import.file_name,
            state='unfinished',
            format=parser.name,
        ))

        bank_country_code = False
        if hasattr(parser, 'country_code'):
            bank_country_code = parser.country_code

        # Results
        results = struct(
            stat_loaded_cnt=0,
            trans_loaded_cnt=0,
            stat_skipped_cnt=0,
            trans_skipped_cnt=0,
            trans_matched_cnt=0,
            bank_costs_invoice_cnt=0,
            error_cnt=0,
            log=[],
        )

        # Caching
        error_accounts = {}
        info = {}
        imported_statement_ids = []

        transaction_ids = []
        for statement in statements:
            if statement.local_account in error_accounts:
                # Don't repeat messages
                results.stat_skipped_cnt += 1
                results.trans_skipped_cnt += len(statement.transactions)
                continue

            # Create fallback currency code
            currency_code = (
                statement.local_currency or company.currency_id.name
            )

            # Check cache for account info/currency
            if statement.local_account in info and \
               currency_code in info[statement.local_account]:
                account_info = info[statement.local_account][currency_code]

            else:
                # Pull account info/currency
                account_info = banktools.get_company_bank_account(
                    self.pool, cr, uid, statement.local_account,
                    statement.local_currency, company, results.log
                )
                if not account_info:
                    results.log.append(
                        _('Statements found for unknown account '
                          '%(bank_account)s') %
                        {
                            'bank_account': statement.local_account
                        }
                    )
                    error_accounts[statement.local_account] = True
                    results.error_cnt += 1
                    continue
                if 'journal_id' not in account_info.keys():
                    results.log.append(
                        _('Statements found for account %(bank_account)s, '
                          'but no default journal was defined.') %
                        {'bank_account': statement.local_account}
                    )
                    error_accounts[statement.local_account] = True
                    results.error_cnt += 1
                    continue

                # Get required currency code
                currency_code = account_info.currency_id.name

                # Cache results
                if statement.local_account not in info:
                    info[statement.local_account] = {
                        currency_code: account_info
                    }
                else:
                    info[statement.local_account][currency_code] = account_info

            # Final check: no coercion of currencies!
            if statement.local_currency \
               and account_info.currency_id.name != statement.local_currency:
                # TODO: convert currencies?
                results.log.append(
                    _('Statement %(statement_id)s for account %(bank_account)s'
                      ' uses different currency than the defined bank '
                      'journal.') %
                    {
                        'bank_account': statement.local_account,
                        'statement_id': statement.id
                    }
                )
                error_accounts[statement.local_account] = True
                results.error_cnt += 1
                continue

            # Check existence of previous statement
            # Less well defined formats can resort to a
            # dynamically generated statement identification
            # (e.g. a datetime string of the moment of import)
            # and have potential duplicates flagged by the
            # matching procedure
            statement_ids = statement_obj.search(cr, uid, [
                ('name', '=', statement.id),
                ('date', '=', convert.date2str(statement.date)),
            ])
            if statement_ids:
                results.log.append(
                    _('Statement %(id)s known - skipped') % {
                        'id': statement.id
                    }
                )
                continue

            # Get the period for the statement (as bank statement object
            # checks this)
            period_ids = period_obj.search(
                cr, uid, [
                    ('company_id', '=', company.id),
                    ('date_start', '<=', statement.date),
                    ('date_stop', '>=', statement.date),
                    ('special', '=', False),
                ], context=context)

            if not period_ids:
                results.log.append(
                    _('No period found covering statement date %(date)s, '
                      'statement %(id)s skipped') % {
                        'date': statement.date,
                        'id': statement.id,
                    }
                )
                continue

            # Create the bank statement record
            statement_id = statement_obj.create(cr, uid, dict(
                name=statement.id,
                journal_id=account_info.journal_id.id,
                date=convert.date2str(statement.date),
                balance_start=statement.start_balance,
                balance_end_real=statement.end_balance,
                balance_end=statement.end_balance,
                state='draft',
                user_id=uid,
                banking_id=import_id,
                company_id=company.id,
                period_id=period_ids[0],
            ))
            imported_statement_ids.append(statement_id)

            subno = 0
            for transaction in statement.transactions:
                subno += 1
                if not transaction.id:
                    transaction.id = str(subno)
                values = {}
                for attr in transaction.__slots__ + ['type']:
                    if attr in import_transaction_obj.column_map:
                        values[import_transaction_obj.column_map[attr]] = \
                            getattr(transaction, attr)
                    elif attr in import_transaction_obj._columns:
                        values[attr] = getattr(transaction, attr)
                values['statement_id'] = statement_id
                values['bank_country_code'] = bank_country_code
                values['local_account'] = statement.local_account
                values['local_currency'] = statement.local_currency

                transaction_id = import_transaction_obj.create(
                    cr, uid, values, context=context)
                transaction_ids.append(transaction_id)

            results.stat_loaded_cnt += 1

        import_transaction_obj.match(
            cr, uid, transaction_ids, results=results, context=context
        )

        # recompute statement end_balance for validation
        statement_obj.button_dummy(
            cr, uid, imported_statement_ids, context=context)

        report = [
            '%s: %s' % (_('Total number of statements'),
                        results.stat_skipped_cnt + results.stat_loaded_cnt),
            '%s: %s' % (_('Total number of transactions'),
                        results.trans_skipped_cnt + results.trans_loaded_cnt),
            '%s: %s' % (_('Number of errors found'),
                        results.error_cnt),
            '%s: %s' % (_('Number of statements skipped due to errors'),
                        results.stat_skipped_cnt),
            '%s: %s' % (_('Number of transactions skipped due to errors'),
                        results.trans_skipped_cnt),
            '%s: %s' % (_('Number of statements loaded'),
                        results.stat_loaded_cnt),
            '%s: %s' % (_('Number of transactions loaded'),
                        results.trans_loaded_cnt),
            '%s: %s' % (_('Number of transactions matched'),
                        results.trans_matched_cnt),
            '%s: %s' % (_('Number of bank costs invoices created'),
                        results.bank_costs_invoice_cnt),
            '',
            '%s:' % (_('Error report')),
            '',
        ]
        text_log = '\n'.join(report + results.log)
        state = results.error_cnt and 'error' or 'ready'
        statement_file_obj.write(cr, uid, import_id, dict(
            state=state,
            log=text_log,
        ), context)
        if not imported_statement_ids or not results.trans_loaded_cnt:
            # file state can be 'ready' while import state is 'error'
            state = 'error'
        self.write(cr, uid, [ids[0]], dict(
            import_id=import_id,
            log=text_log,
            state=state,
            statement_ids=[(6, 0, imported_statement_ids)],
        ), context)
        return {
            'name': (state == 'ready' and _('Review Bank Statements') or
                     _('Error')),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': self._name,
            'domain': [],
            'context': dict(context, active_ids=ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': ids[0] or False,
        }

    _columns = {
        'company': fields.many2one(
            'res.company', 'Company', required=True,
            states={
                'ready': [('readonly', True)],
                'error': [('readonly', True)],
            },
        ),
        'file_name': fields.char('File name', size=256),
        'file': fields.binary(
            'Statements File',
            required=True,
            help=('The Transactions File to import. Please note that while it '
                  'is perfectly safe to reload the same file multiple times '
                  'or to load in timeframe overlapping statements files, '
                  'there are formats that may introduce different '
                  'sequencing, which may create double entries.\n\n'
                  'To stay on the safe side, always load bank statements '
                  'files using the same format.'),
            states={
                'ready': [('readonly', True)],
                'error': [('readonly', True)],
            },
        ),
        'parser': fields.selection(
            parser_types, 'File Format', required=True,
            states={
                'ready': [('readonly', True)],
                'error': [('readonly', True)],
            },
        ),
        'log': fields.text('Log', readonly=True),
        'state': fields.selection(
            [
                ('init', 'init'),
                ('ready', 'ready'),
                ('error', 'error')
            ],
            'State', readonly=True),
        'import_id': fields.many2one(
            'account.banking.imported.file', 'Import File'),
        'statement_ids': fields.many2many(
            'account.bank.statement', 'rel_wiz_statements', 'wizard_id',
            'statement_id', 'Imported Bank Statements'),
        'line_ids': fields.one2many(
            'banking.import.line', 'banking_import_id', 'Transactions',
        ),
    }

    def _default_parser_type(self, cr, uid, context=None):
        types = models.parser_type.get_parser_types()
        return types and types[0][0] or False

    _defaults = {
        'state': 'init',
        'company': lambda s, cr, uid, c:
            s.pool.get('res.company')._company_default_get(
                cr, uid, 'bank.import.transaction', context=c),
        'parser': _default_parser_type,
    }
