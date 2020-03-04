import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-bank-payment",
    description="Meta package for oca-bank-payment Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-account_banking_mandate',
        'odoo10-addon-account_banking_mandate_sale',
        'odoo10-addon-account_banking_pain_base',
        'odoo10-addon-account_banking_sepa_credit_transfer',
        'odoo10-addon-account_banking_sepa_direct_debit',
        'odoo10-addon-account_payment_line_cancel',
        'odoo10-addon-account_payment_mode',
        'odoo10-addon-account_payment_order',
        'odoo10-addon-account_payment_partner',
        'odoo10-addon-account_payment_purchase',
        'odoo10-addon-account_payment_sale',
        'odoo10-addon-account_voucher_killer',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
