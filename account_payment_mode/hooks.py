# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def pre_init_hook(cr):
    migrate_from_8(cr)


def migrate_from_8(cr):
    """If we're installed on a database which has the payment_mode table
    from 8.0, move its table so that we use the already existing modes"""
    cr.execute("SELECT 1 FROM pg_class WHERE relname = 'payment_mode'")
    if not cr.fetchone():
        return
    try:
        from openupgradelib.openupgrade import rename_models, rename_tables
        rename_models(cr, [('payment.mode', 'account.payment.mode')])
        rename_tables(cr, [('payment_mode', 'account_payment_mode')])
    except ImportError:
        cr.execute('ALTER TABLE payment_mode RENAME TO account_payment_mode')
        cr.execute('ALTER SEQUENCE payment_mode_id_seq '
                   'RENAME TO account_payment_mode_id_seq')
    # Set fixed bank account in all, which is the equivalent behavior in v8
    cr.execute(
        "ALTER TABLE account_payment_mode ADD bank_account_link VARCHAR"
    )
    cr.execute("UPDATE account_payment_mode SET bank_account_link='fixed'")
    cr.execute(
        'ALTER TABLE account_payment_mode '
        'RENAME COLUMN journal TO fixed_journal_id'
    )
