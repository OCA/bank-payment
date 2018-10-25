import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-bank-payment",
    description="Meta package for oca-bank-payment Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-account_banking_mandate',
        'odoo11-addon-account_banking_pain_base',
        'odoo11-addon-account_banking_sepa_credit_transfer',
        'odoo11-addon-account_banking_sepa_direct_debit',
        'odoo11-addon-account_payment_mode',
        'odoo11-addon-account_payment_order',
        'odoo11-addon-account_payment_order_return',
        'odoo11-addon-account_payment_partner',
        'odoo11-addon-account_payment_purchase',
        'odoo11-addon-account_payment_sale',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
