##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsability of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs
#    End users who are looking for a ready-to-use solution with commercial
#    garantees and support are strongly adviced to contract EduSense BV
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Account Banking NL ClieOp',
    'version': '0.1',
    'license': 'GPL-3',
    'author': 'EduSense BV',
    'website': 'http://www.edusense.nl',
    'category': 'Account Banking',
    'depends': ['account_banking'],
    'init_xml': [],
    'update_xml': [
        #'security/ir.model.access.csv',
        'account_banking_nl_clieop.xml',
        'account_banking_export_wizard.xml',
        'data/banking_export_clieop.xml',
    ],
    'demo_xml': [],
    'description': '''
    Module to export payment orders in ClieOp format.

    ClieOp format is used by Dutch banks to batch national bank transfers.
    This module uses the account_banking logic.
    ''',
    'active': False,
    'installable': True,
}
