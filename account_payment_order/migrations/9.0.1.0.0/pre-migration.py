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

# They are being handled after module rename, so source module name is correct
EXISTING_PAYMENT_MODE_TYPE_XML_IDS = {
    'account_payment_order.manual_bank_tranfer': (
        'account.account_payment_method_manual_out',
    ),
    'account_payment_order.manual_direct_debit': (
        'account.account_payment_method_manual_in',
    ),
}

TO_CREATE_PAYMENT_MODE_TYPE_XML_IDS = {
    'account_banking_sepa_direct_debit.export_sdd_008_001_02': (
        'account_banking_sepa_direct_debit.sepa_direct_debit',
    ),
    'account_banking_sepa_credit_transfer.export_sepa_sct_001_001_03': (
        'account_banking_sepa_credit_transfer.sepa_credit_transfer',
    ),
}


def install_new_modules(cr):
    sql = """
    UPDATE ir_module_module
    SET state='to install'
    WHERE name in %s AND state='uninstalled'
    """ % (tuple(to_install),)
    openupgrade.logged_query(cr, sql)


def migrate_payment_mode_types(env):
    """Create payment methods for each old payment type defined, and assign it
     on payment modes."""
    payment_method_obj = env['account.payment.method']
    imr_obj = env['ir.model.data']
    # Add a column in payment method for storing old payment_mode_type ID
    old_column_name = openupgrade.get_legacy_name('payment_mode_type_id')
    env.cr.execute(
        "ALTER TABLE account_payment_method ADD %s INTEGER" % old_column_name
    )
    env.cr.execute(
        """SELECT id, name, code, payment_order_type, active
        FROM payment_mode_type
        """
    )
    for row in env.cr.fetchall():
        # Look if this type has a key XML-ID for not duplicating records with
        # the same goal
        imr = imr_obj.search([
            ('res_id', '=', row[0]),
            ('model', '=', 'payment_mode_type'),
        ])
        xml_id = "%s.%s" % (imr.module, imr.name)
        if xml_id in EXISTING_PAYMENT_MODE_TYPE_XML_IDS:
            method = env.ref(EXISTING_PAYMENT_MODE_TYPE_XML_IDS[xml_id])
        else:
            method = payment_method_obj.create({
                'name': row[1],
                'code': row[2],
                'payment_type': (
                    'outbound' if row[3] == 'payment' else 'outbound'
                ),
                'active': row[4],
            })
        env.cr.execute(
            "UPDATE account_payment_method SET %s = %%s" % old_column_name,
            (method.id, ),
        )
        if xml_id in TO_CREATE_PAYMENT_MODE_TYPE_XML_IDS:
            # Create XML-ID for this yet non existing records
            mod, name = TO_CREATE_PAYMENT_MODE_TYPE_XML_IDS[xml_id].split('.')
            imr_obj.create({
                'module': mod,
                'name': name,
                'res_id': method.id,
                'model': method._name,
            })
        openupgrade.logged_query(
            env.cr,
            """UPDATE account_payment_mode
            SET payment_method_id = %s
            WHERE type = %s""",
            (method.id, row[0]),
        )


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
        migrate_payment_mode_types(env)

    if openupgrade.is_module_installed(
            env.cr, 'account_banking_payment_transfer'):
        openupgrade.rename_columns(env.cr, column_renames_payment_transfer)
        openupgrade.update_module_names(
            env.cr,
            [('account_banking_payment_transfer', 'account_payment_order')],
            merge_modules=True)
    openupgrade.rename_models(env.cr, models_renames)
    openupgrade.rename_tables(env.cr, table_renames)
