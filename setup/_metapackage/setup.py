import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-bank-payment",
    description="Meta package for oca-bank-payment Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-account_banking_mandate',
        'odoo8-addon-account_banking_pain_base',
        'odoo8-addon-account_banking_payment_export',
        'odoo8-addon-account_banking_payment_transfer',
        'odoo8-addon-account_banking_sepa_credit_transfer',
        'odoo8-addon-account_banking_sepa_direct_debit',
        'odoo8-addon-account_banking_tests',
        'odoo8-addon-account_direct_debit',
        'odoo8-addon-account_import_line_multicurrency_extension',
        'odoo8-addon-account_payment_blocking',
        'odoo8-addon-account_payment_include_draft_move',
        'odoo8-addon-account_payment_mode_term',
        'odoo8-addon-account_payment_partner',
        'odoo8-addon-account_payment_purchase',
        'odoo8-addon-account_payment_sale',
        'odoo8-addon-account_payment_sale_stock',
        'odoo8-addon-account_payment_transfer_reconcile_batch',
        'odoo8-addon-account_voucher_killer',
        'odoo8-addon-portal_payment_mode',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
