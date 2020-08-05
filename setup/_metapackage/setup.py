import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-bank-payment",
    description="Meta package for oca-bank-payment Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-account_banking_mandate',
        'odoo13-addon-account_banking_pain_base',
        'odoo13-addon-account_banking_sepa_credit_transfer',
        'odoo13-addon-account_banking_sepa_direct_debit',
        'odoo13-addon-account_payment_mode',
        'odoo13-addon-account_payment_order',
        'odoo13-addon-account_payment_partner',
        'odoo13-addon-account_payment_purchase',
        'odoo13-addon-account_payment_purchase_stock',
        'odoo13-addon-account_payment_sale',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
