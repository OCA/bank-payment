import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-bank-payment",
    description="Meta package for oca-bank-payment Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_banking_mandate>=15.0dev,<15.1dev',
        'odoo-addon-account_banking_mandate_contact>=15.0dev,<15.1dev',
        'odoo-addon-account_banking_mandate_sale>=15.0dev,<15.1dev',
        'odoo-addon-account_banking_pain_base>=15.0dev,<15.1dev',
        'odoo-addon-account_banking_sepa_credit_transfer>=15.0dev,<15.1dev',
        'odoo-addon-account_banking_sepa_direct_debit>=15.0dev,<15.1dev',
        'odoo-addon-account_payment_mode>=15.0dev,<15.1dev',
        'odoo-addon-account_payment_order>=15.0dev,<15.1dev',
        'odoo-addon-account_payment_order_grouped_output>=15.0dev,<15.1dev',
        'odoo-addon-account_payment_partner>=15.0dev,<15.1dev',
        'odoo-addon-account_payment_purchase>=15.0dev,<15.1dev',
        'odoo-addon-account_payment_purchase_stock>=15.0dev,<15.1dev',
        'odoo-addon-account_payment_sale>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
