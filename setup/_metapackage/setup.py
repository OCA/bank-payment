import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-bank-payment",
    description="Meta package for oca-bank-payment Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-account_banking_mandate',
        'odoo9-addon-account_banking_mandate_sale',
        'odoo9-addon-account_banking_pain_base',
        'odoo9-addon-account_banking_sepa_credit_transfer',
        'odoo9-addon-account_banking_sepa_direct_debit',
        'odoo9-addon-account_payment_mode',
        'odoo9-addon-account_payment_order',
        'odoo9-addon-account_payment_order_return',
        'odoo9-addon-account_payment_partner',
        'odoo9-addon-account_payment_purchase',
        'odoo9-addon-account_payment_sale',
        'odoo9-addon-account_payment_transfer_reconcile_batch',
        'odoo9-addon-portal_payment_mode',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
