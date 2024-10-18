# Copyright 2010-2020 Akretion (www.akretion.com)
# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Account Banking SEPA Credit Transfer",
    "summary": "Create SEPA XML files for Credit Transfers",
    "version": "16.0.1.1.5",
    "license": "AGPL-3",
    "author": "Akretion, Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "category": "Banking addons",
    "conflicts": ["account_sepa"],
    "depends": ["account_banking_pain_base"],
    "data": ["data/account_payment_method.xml"],
    "demo": ["demo/sepa_credit_transfer_demo.xml"],
    "installable": True,
}
