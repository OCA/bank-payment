# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Blocking module for OpenERP
#    Copyright (C) 2014 ACSONE SA/NV (http://acsone.eu)
#    @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
#    @author Adrien Peiffer <adrien.peiffer@acsone.eu>
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
    'name': 'account banking payment blocking',
    'version': '0.1',
    'category': 'Banking addons',
    'description': """
    Prevent invoices under litigation to be proposed in payment orders.

    This module uses the 'blocked' flag that is present on move lines,
    to filter out lines proposed in payment orders.

    In addition it exposes this flag on the supplier invoice form
    so it is easier to block an invoice.
    """,
    'author': 'ACSONE SA/NV',
    'website': 'http://acsone.eu',
    'depends': [
        'base',
        'account_banking_payment_export'
    ],
    'data': [
        'view/account_invoice_view.xml'
    ],
    'test': [
    ],
    'demo': [
    ],
    'js': [
    ],
    'qweb': [
    ],
    'css': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
