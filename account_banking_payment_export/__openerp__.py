# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#              (C) 2013 - 2014 ACSONE SA (<http://acsone.eu>).
#
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
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
    'version': '7.0.0.1.166',
    'license': 'AGPL-3',
    'author': "Banking addons community,Odoo Community Association (OCA)",
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': [
        'account_payment',
        'base_iban',  # for manual_bank_tranfer
    ],
    'conflicts': [
        # lp:account-payment/account_payment_extension also adds
        # a type field to payment.mode, with a very similar purpose.
        # We can't add a dependency on account_payment_extension here
        # because account_payment_extension adds many other features
        # that probably conflict with other parts of lp:banking-addons.
        # Proposal to resolve: make account_payment_extension depend
        # on the present account_banking_payment_export module.
        'account_payment_extension',
    ],
    'data': [
        'view/account_payment.xml',
        'view/bank_payment_manual.xml',
        'view/payment_mode.xml',
        'view/payment_mode_type.xml',
        'view/payment_order_create_view.xml',
        'data/payment_mode_type.xml',
        'security/ir.model.access.csv',
    ],
    'demo': ['demo/banking_demo.xml'],
    'description': '''
        Infrastructure to export payment orders
        plus some bug fixes and obvious enhancements to payment orders
        that will hopefully land in offical addons one day.

        This technical module provides the base infrastructure to export
        payment orders for electronic banking. It provides the following
        technical features:
        * a new payment.mode.type model
        * payment.mode now has a mandatory type
        * a better implementation of payment_mode.suitable_bank_types() based
          on payment.mode.type
        * the "make payment" button launches a wizard depending on the
          payment.mode.type
        * a manual payment mode type is provided as an example, with a default
          "do nothing" wizard

        To enable the use of payment order to collect money for customers,
        it adds a payment_order_type (payment|debit) as a basis of direct debit
        support (this field becomes visible when account_direct_debit is
        installed).
        Refactoring note: this field should ideally go in account_direct_debit,
        but account_banking_payment currently depends on it.

        Bug fixes and enhancement that should land in official addons:
        * make the search function of the payment export wizard extensible
        * fix lp:1275478: allow payment of customer refunds
        * display the maturity date of the move lines when you are in
          the wizard to select the lines to pay
''',
    'installable': True,
}
