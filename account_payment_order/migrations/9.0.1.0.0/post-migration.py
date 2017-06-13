# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def map_payment_type(cr):
    openupgrade.map_values(
        cr,
        'payment_order_type', 'payment_type', [
            ('payment', 'outbound'),
            ('debit', 'inbound'),
        ],
        table='account_payment_order', write='sql')

    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('state'), 'state',
        [('done', 'uploaded'), ('sent', 'generated')],
        table='account_payment_order', write='sql')


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    map_payment_type(cr)

    cr.execute("""
       UPDATE account_payment_order apo
       SET journal_id=apm.fixed_journal_id
       FROM account_payment_mode apm
       WHERE apo.payment_mode_id = apm.id
    """)
