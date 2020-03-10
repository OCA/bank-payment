import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-bank-payment",
    description="Meta package for oca-bank-payment Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-account_payment_mode',
        'odoo13-addon-account_payment_partner',
        'odoo13-addon-account_payment_sale',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
