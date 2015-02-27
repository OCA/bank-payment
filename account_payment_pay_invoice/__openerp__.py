# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment that pays invoices module for OpenERP
#    Copyright (C) 2015 VisionDirect (http://www.visiondirect.co.uk)
#    @author Matthieu Choplin <matthieu.choplin@visiondirect.co.uk>
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
    'name': 'Account Payment that pays invoices',
    'version': '0.1',
    "sequence": 14,
    'complexity': "easy",
    'category': 'Payment',
    'description': """
        Complete the payment workflow by simulating
        a bank statement reconciliation.
        We know that an invoice is going to be marked "paid" when the functional fields "reconciled" is going to be true.
        And it is going to be True once all the account_move_line linked to the account_invoice are reconciled, aka once
        all the account_move_line linked to the account_invoice are linked to account_move_reconcile through the
        field reconcile_id
    """,
    'author': 'Visiondirect',
    'website': 'visiondirect.co.uk',
    'depends': ["account_payment"],
    'data': [
        "view/account_payment_view.xml",
    ],
    'test': [
        'test/test_payment_method.yml',
        'test/test_payment_method_multicurrency.yml',
        'test/test_payment_method_partial.yml',
    ],
    'installable': True,
    'auto_install': False,
    'contributors': ['Matthieu Choplin <matthieu.choplin@visiondirect.co.uk>'],
}
