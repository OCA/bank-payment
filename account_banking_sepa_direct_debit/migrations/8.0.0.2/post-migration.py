# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Akretion (http://www.akretion.com/)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp import pooler, SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return

    pool = pooler.get_pool(cr.dbname)
    cr.execute('''
        SELECT
        old_sepa.file,
        rel.account_order_id AS payment_order_id,
        payment_order.reference
        FROM migration_banking_export_sdd old_sepa
        LEFT JOIN migration_account_payment_order_sdd_rel rel
        ON old_sepa.id=rel.banking_export_sepa_id
        LEFT JOIN payment_order ON payment_order.id=rel.account_order_id
        ''')

    for sepa_file in cr.dictfetchall():
        filename = 'sdd_%s.xml' % sepa_file['reference'].replace('/', '-')
        pool['ir.attachment'].create(
            cr, SUPERUSER_ID, {
                'name': filename,
                'res_id': sepa_file['payment_order_id'],
                'res_model': 'payment.order',
                'datas': str(sepa_file['file']),
                })
    return
