# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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
    'name': 'Account Banking Aggregate Payment',
    'version': '0.1.173',
    'license': 'AGPL-3',
    'author': "Therp BV,Odoo Community Association (OCA)",
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': ['account_direct_debit'],
    'data': [
        'data/payment_mode_type.xml',
        'view/payment_mode.xml',
        'view/export_aggregate.xml',
        ],
    'description': '''
    This module allows for aggregating payments for various creditors
    and making them payable to a single partner. This is practiced in
    certain purchasing consortia.

    After collection of the payable invoices on a payment order of type
    'Aggregate payment', the move lines in the payment order are
    reconciled by a move on a transit account, the total amount of which
    is then transferred onto the designated partner's account payable
    (upon confirmation of the aggregate payment order).

    The payment order wizard then proceeds to create a new payment order
    of a user chosen payment mode with only the aggregate move line in it.
    ''',
    'active': False,
}
