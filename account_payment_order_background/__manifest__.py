# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Payment Order in Background',
    'summary': 'The reconciliation of move lines from payment order '
               'is processed in jobs.',
    'version': '12.0.1.0.0',
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': [
        'account_payment_order',
        'queue_job',
    ],
    'website': 'https://www.camptocamp.com',
    'data': [],
    'installable': True,
}
