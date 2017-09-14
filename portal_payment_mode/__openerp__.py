# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Sergio Teruel
# Copyright 2017 Tecnativa - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': "Portal Payment Mode",
    'summary': "Adds payment mode ACL's for portal users ",
    'category': 'Portal',
    'version': '9.0.1.0.0',
    'depends': [
        'portal_sale',
        'account_payment_partner',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://www.tecnativa.com',
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': True,
    'application': False,
}
