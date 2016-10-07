# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import pooler, SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return

    pool = pooler.get_pool(cr.dbname)
    cr.execute('''
        SELECT
        old_sepa.file,
        rel.account_order_id AS payment_order_id,
        payment_order.reference
        FROM migration_banking_export_sepa old_sepa
        LEFT JOIN migration_account_payment_order_sepa_rel rel
        ON old_sepa.id=rel.banking_export_sepa_id
        LEFT JOIN payment_order ON payment_order.id=rel.account_order_id
        ''')

    for sepa_file in cr.dictfetchall():
        if not sepa_file['payment_order_id']:
            continue
        filename = 'sct_%s.xml' % sepa_file['reference'].replace('/', '-')
        pool['ir.attachment'].create(
            cr, SUPERUSER_ID, {
                'name': filename,
                'res_id': sepa_file['payment_order_id'],
                'res_model': 'payment.order',
                'datas': str(sepa_file['file']),
                })
    return
