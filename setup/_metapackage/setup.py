import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-bank-payment",
    description="Meta package for oca-bank-payment Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-account_banking_mandate',
        'odoo14-addon-account_banking_mandate_sale',
        'odoo14-addon-account_banking_pain_base',
        'odoo14-addon-account_banking_sepa_credit_transfer',
        'odoo14-addon-account_banking_sepa_direct_debit',
        'odoo14-addon-account_invoice_select_for_payment',
        'odoo14-addon-account_payment_mode',
        'odoo14-addon-account_payment_order',
        'odoo14-addon-account_payment_order_return',
        'odoo14-addon-account_payment_partner',
        'odoo14-addon-account_payment_purchase',
        'odoo14-addon-account_payment_purchase_stock',
        'odoo14-addon-account_payment_sale',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
