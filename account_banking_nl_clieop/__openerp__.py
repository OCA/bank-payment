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
{
    'name': 'Account Banking NL ClieOp',
    'version': '0.92',
    'license': 'AGPL-3',
    'author': "EduSense BV,Odoo Community Association (OCA)",
    'website': 'http://www.edusense.nl',
    'category': 'Account Banking',
    'depends': [
        'account_banking_payment',
        'account_iban_preserve_domestic',
    ],
    'data': [
        'account_banking_nl_clieop.xml',
        'wizard/export_clieop_view.xml',
        'data/banking_export_clieop.xml',
        'security/ir.model.access.csv',
    ],
    'description': '''
    Module to export payment orders in ClieOp format.

    ClieOp format is used by Dutch banks to batch national bank transfers.
    This module uses the account_banking logic.
    ''',
    'installable': False,
}
