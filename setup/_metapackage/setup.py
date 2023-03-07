import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-bank-payment",
    description="Meta package for oca-bank-payment Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_payment_mode>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_order>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_order_grouped_output>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_partner>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_sale>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
