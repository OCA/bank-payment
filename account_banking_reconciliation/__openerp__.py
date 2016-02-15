# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
{
    'name': 'Bank Account Reconciliation',
    'version': '8.0.1.7.0',
    'license': 'AGPL-3',
    'category': 'Accounting and Financial Management',
    'author': 'NovaPoint Group LLC, Odoo Community Association (OCA)',
    'website': ' http://www.novapointgroup.com',
    'depends': [
        'account_cutoff_base',
        'account_voucher',
        'report_webkit',
    ],
    'data': [
        "security/account_banking_reconciliation_security.xml",
        "security/ir.model.access.csv",
        "views/bank_acc_rec_statement.xml",
        "views/account_move_line_view.xml",
        "report/report.xml",
    ],
    'installable': True,
}
