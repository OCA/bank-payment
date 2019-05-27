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
    # Populate these missing related fields
    openupgrade.logged_query(
        cr, """
        UPDATE bank_payment_line bpl
        SET payment_type = apo.payment_type,
            state = apo.state
        FROM account_payment_order apo
        WHERE bpl.order_id = apo.id""",
    )
    openupgrade.logged_query(
        cr, """
        UPDATE account_payment_line apl
        SET payment_type = apo.payment_type,
            state = apo.state
        FROM account_payment_order apo
        WHERE apl.order_id = apo.id""",
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    table = 'account_payment_order'
    if (openupgrade.table_exists(cr, table) and
            openupgrade.column_exists(cr, table, 'payment_order_type')):
        map_payment_type(cr)

    cr.execute("""
       UPDATE account_payment_order apo
       SET journal_id=apm.fixed_journal_id
       FROM account_payment_mode apm
       WHERE apo.payment_mode_id = apm.id
    """)
