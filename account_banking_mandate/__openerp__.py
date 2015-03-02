# -*- encoding: utf-8 -*-
##############################################################################
#
#    Mandate module for openERP
#    Copyright (C) 2014 Compassion CH (http://www.compassion.ch)
#    @author: Cyril Sester <csester@compassion.ch>,
#             Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Account Banking Mandate',
    'summary': 'Banking mandates',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': "Compassion CH,Odoo Community Association (OCA)",
    'website': 'http://www.compassion.ch',
    'category': 'Banking addons',
    'depends': ['account_payment'],
    'external_dependencies': {},
    'data': [
        'view/account_banking_mandate_view.xml',
        'view/account_invoice_view.xml',
        'view/account_payment_view.xml',
        'view/res_partner_bank_view.xml',
        'data/mandate_reference_sequence.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': ['test/banking_mandate.yml'],
    'description': '''
    This module adds a generic model for banking mandates.
    These mandates can be specialized to fit any banking mandates (such as
    sepa or lsv).

    A banking mandate is attached to a bank account and represents an
    authorization that the bank account owner gives to a company for a
    specific operation (such as direct debit).
    You can setup mandates from the accounting menu or directly from a bank
    account.
''',
    'active': False,
    'installable': True,
}
