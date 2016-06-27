# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': "Portal Payment Mode",
    'summary': "Adds payment mode ACL's for portal users ",
    'category': 'Portal',
    'version': '8.0.1.0.0',
    'depends': [
        'portal_sale',
        'account_payment_partner',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'author': 'Antiun Ingeniería S.L., '
              'Incaser Informatica S.L., '
              'Odoo Community Association (OCA)',
    'website': 'http://www.antiun.com',
    'license': 'AGPL-3',
    'installable': False,
    'auto_install': True,
    'application': False,
}
