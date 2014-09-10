# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 Therp BV (<http://therp.nl>).
#              (C) 2011 Smile (<http://smile.fr>).
#
#    All other contributions are (C) by their respective contributors
#
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

{
    'name': 'Account Banking',
    'version': '0.4',
    'license': 'AGPL-3',
    'author': 'Banking addons community',
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': [
        'account_voucher',
        ],
    'data': [
        'security/ir.model.access.csv',
        'data/account_banking_data.xml',
        'wizard/bank_import_view.xml',
        'account_banking_view.xml',
        'wizard/banking_transaction_wizard.xml',
        'wizard/link_partner.xml',
        'workflow/account_invoice.xml',
    ],
    'js': [
        'static/src/js/account_banking.js',
    ],
    'description': '''
    Module to do banking.

    This modules tries to combine all current banking import and export
    schemes. Rationale for this is that it is quite common to have foreign
    bank account numbers next to national bank account numbers. The current
    approach, which hides the national banking interface schemes in the
    l10n_xxx modules, makes it very difficult to use these simultanious.
    A more banking oriented approach seems more logical and cleaner.

    Changes to default OpenERP:

    * Puts focus on the real life messaging with banks:
      + Bank statement lines upgraded to independent bank transactions.
      + Banking statements have no special accountancy meaning, they're just
        message envelopes for a number of bank transactions.
      + Bank statements can be either encoded by hand to reflect the document
        version of Bank Statements, or created as an optional side effect of
        importing Bank Transactions.

    * Preparations for SEPA:
      + IBAN accounts are the standard in the SEPA countries
      + local accounts are derived from SEPA (excluding Turkey) but are
        considered to be identical to the corresponding SEPA account.
      + Banks are identified with either Country + Bank code + Branch code or
        BIC
      + Each bank can have its own pace in introducing SEPA into their
        communication with their customers.
      + National online databases can be used to convert BBAN's to IBAN's.
      + The SWIFT database is consulted for bank information.

    * Adds dropin extensible import facility for bank communication in:
      - Drop-in input parser development.
      - MultiBank (NL) format transaction files available as
        account_banking_nl_multibank,

    * Extends payments for digital banking:
      + Adapted workflow in payments to reflect banking operations
      + Relies on account_payment mechanics to extend with export generators.
      - ClieOp3 (NL) payment and direct debit orders files available as
        account_banking_nl_clieop

    * Additional features for the import/export mechanism:
      + Automatic matching and creation of bank accounts, banks and partners,
        during import of statements.
      + Automatic matching with invoices and payments.
      + Sound import mechanism, allowing multiple imports of the same
        transactions repeated over multiple files.
      + Journal configuration per bank account.
      + Business logic and format parsing strictly separated to ease the
        development of new parsers.
      + No special configuration needed for the parsers, new parsers are
        recognized and made available at server (re)start.
    ''',
    'installable': False,
    'auto_install': False,
}
