# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#              (C) 2013 - 2014 ACSONE SA (<http://acsone.eu>).
#
#    All other contributions are (C) by their respective contributors
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
    'name': 'Account Banking - Payments Export Infrastructure',
    'version': '8.0.0.1.166',
    'license': 'AGPL-3',
    'author': "ACSONE SA/NV, "
              "Therp BV, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/bank-payment',
    'category': 'Banking addons',
    'depends': [
        'account_payment',
        'base_iban',  # for manual_bank_tranfer
        'document',  # to see the attachments on payment.order
    ],
    'data': [
        'views/account_payment.xml',
        'views/payment_mode.xml',
        'views/payment_mode_type.xml',
        'wizard/bank_payment_manual.xml',
        'wizard/payment_order_create_view.xml',
        'data/payment_mode_type.xml',
        'workflow/account_payment.xml',
        'security/ir.model.access.csv',
    ],
    'demo': ['demo/banking_demo.xml'],
    'installable': True,
}
