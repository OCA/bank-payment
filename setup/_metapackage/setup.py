import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-bank-payment",
    description="Meta package for oca-bank-payment Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_banking_mandate>=16.0dev,<16.1dev',
        'odoo-addon-account_banking_mandate_contact>=16.0dev,<16.1dev',
        'odoo-addon-account_banking_mandate_sale>=16.0dev,<16.1dev',
        'odoo-addon-account_banking_mandate_sale_contact>=16.0dev,<16.1dev',
        'odoo-addon-account_banking_pain_base>=16.0dev,<16.1dev',
        'odoo-addon-account_banking_sepa_credit_transfer>=16.0dev,<16.1dev',
        'odoo-addon-account_banking_sepa_direct_debit>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_method_fs_storage>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_mode>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_order>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_order_grouped_output>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_order_notification>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_order_return>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_order_tier_validation>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_order_vendor_email>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_partner>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_purchase>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_purchase_stock>=16.0dev,<16.1dev',
        'odoo-addon-account_payment_sale>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
