import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-bank-payment",
    description="Meta package for oca-bank-payment Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_payment_mode>=15.0dev,<15.1dev',
        'odoo-addon-account_payment_order>=15.0dev,<15.1dev',
        'odoo-addon-account_payment_partner>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
