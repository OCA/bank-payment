import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-bank-payment",
    description="Meta package for oca-bank-payment Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-account_banking_mandate',
        'odoo14-addon-account_banking_pain_base',
        'odoo14-addon-account_banking_sepa_credit_transfer',
        'odoo14-addon-account_payment_mode',
        'odoo14-addon-account_payment_order',
        'odoo14-addon-account_payment_partner',
        'odoo14-addon-account_payment_purchase',
        'odoo14-addon-account_payment_purchase_stock',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
