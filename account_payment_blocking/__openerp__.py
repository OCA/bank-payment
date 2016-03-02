# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Blocking module for Odoo
#    Copyright (C) 2014-2015 ACSONE SA/NV (http://acsone.eu)
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
    'version': '8.0.1.0.0',
    'category': 'Banking addons',
    'summary': """
        Prevent invoices under litigation to be proposed in payment orders.
    """,
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'http://acsone.eu',
    'depends': [
        'base',
        'account_banking_payment_export'
    ],
    'data': [
        'view/account_invoice_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
