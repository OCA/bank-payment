# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
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
    "name": "Bank statement instant voucher",
    "version": "1.0r028",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "category": 'Base',
    'complexity': "normal",
    "description": """
This module adds a new button on the bank statement line that allows the
accountant to instantly create a sales or purchase voucher based on the
values of the bank statement line.

This module does not depend on account_banking, but if this module is
installed, the bank statement line will be reconciled automatically
in the confirmation step of the wizard.

If account_banking is not installed, the accountant will still have to
reconcile the associated move line with the move line from the bank
statement line manually.

If the wizard is cancelled,the created voucher will be deleted again.

Known limitations:

Currency conversion and payment difference writeoff are not yet
supported.
    """,
    'website': 'http://therp.nl',
    'images': [],
    'depends': [
        'account_voucher',
    ],
    'data': [
        'view/account_voucher_instant.xml',
        'view/account_bank_statement_line.xml',
    ],
    "license": 'AGPL-3',
}
