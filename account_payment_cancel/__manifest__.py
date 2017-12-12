{
    'name': 'Account payment cancel',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Monzione Marco',
    'website': 'https://www.compassion.ch',
    'category': 'Banking addons',
    'depends': [
        'account_payment_order',
    ],
    'data': [
        'views/invoice_view.xml',
    ],
    'demo': [
        'res/test_data.yml',
    ],
    'test': [

    ],
    'installable': True,
}
