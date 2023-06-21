# Copyright 2023 Compassion CH (<https://www.compassion.ch>)
# @author: Simon Gonzalez <simon.gonzalez@bluewin.ch>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Payment Export via SFTP",
    "version": "14.0.1.0.0",
    "development_status": "Beta",
    "license": "AGPL-3",
    "author": "Compassion CH,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "category": "Banking addons",
    "depends": [
        "account_payment_order",
        "edi_storage_oca",  # OCA/edi
        "storage_backend_sftp",  # OCA/storage
        "account_payment_return_import_iso20022",  # OCA/account-payment
    ],
    "data": ["views/account_payment_order_view.xml"],
    "installable": True,
}
