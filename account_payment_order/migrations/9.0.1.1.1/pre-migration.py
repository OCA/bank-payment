# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

# V9 modules that don't exist in v8 and are dependent of
# account_payment_order
to_install = [
    'account_payment_mode',
    'account_payment_partner',
]

table_renames = [
    ('payment_order', 'account_payment_order'),
    ('payment_line', 'account_payment_line'),
]

models_renames = [
    ('payment.order', 'account.payment.order'),
    ('payment.line', 'account.payment.line'),
]

column_renames_account_payment = {
    'payment_order': [
        ('reference', 'name'),
        ('mode', 'payment_mode_id'),
        ('user_id', 'generated_user_id'),
        ('date_created', 'date_generated'),
        ('date_done', None),
        ('state', None),
    ],
    'payment_line': [
        ('currency', 'currency_id'),
        ('company_currency', 'company_currency_id'),
        ('bank_id', 'partner_bank_id'),
    ],
}

column_renames_payment_export = {
    'payment_order': [
        ('total', 'total_company_currency'),
    ],
}

column_renames_payment_transfer = {
    'account_payment_mode': [
        ('transfer_move_option', 'move_option'),
    ],
    'payment_order': [
        ('date_sent', 'date_uploaded'),
    ],
    'payment_line': [
        ('msg', None),
        ('date_done', None),
    ],
    'bank_payment_line': [
        ('transit_move_line_id', None),
    ],
}


def install_new_modules(cr):
    sql = """
    UPDATE ir_module_module
    SET state='to install'
    WHERE name in %s AND state='uninstalled'
    """ % (tuple(to_install),)
    openupgrade.logged_query(cr, sql)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    install_new_modules(env.cr)
    openupgrade.rename_columns(env.cr, column_renames_account_payment)

    if openupgrade.is_module_installed(env.cr, 'account_direct_debit'):
        openupgrade.update_module_names(
            env.cr,
            [('account_direct_debit', 'account_payment_order')],
            merge_modules=True)

    if openupgrade.is_module_installed(
            env.cr, 'account_banking_payment_export'):
        openupgrade.update_module_names(
            env.cr,
            [('account_banking_payment_export', 'account_payment_order')],
            merge_modules=True)
        openupgrade.rename_columns(env.cr, column_renames_payment_export)

    if openupgrade.is_module_installed(
            env.cr, 'account_banking_payment_transfer'):
        openupgrade.rename_columns(env.cr, column_renames_payment_transfer)
        openupgrade.update_module_names(
            env.cr,
            [('account_banking_payment_transfer', 'account_payment_order')],
            merge_modules=True)
    openupgrade.rename_models(env.cr, models_renames)
    openupgrade.rename_tables(env.cr, table_renames)
