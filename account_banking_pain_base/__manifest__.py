# Copyright 2013-2022 Akretion - Alexis de Lattre
# Copyright 2014-2022 Tecnativa - Pedro M. Baeza
# Copyright 2016-2022 Tecnativa - Antonio Espinosa
# Copyright 2021-2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Banking PAIN Base Module",
    "summary": "Base module for PAIN file generation",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion, Noviat, Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "category": "Hidden",
    "depends": ["account_payment_order"],
    "external_dependencies": {"python": ["unidecode", "lxml"]},
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/iso20022.code.list.csv",
        "views/account_payment_line.xml",
        "views/account_payment_order.xml",
        "views/bank_payment_line.xml",
        "views/account_payment_mode.xml",
        "views/res_config_settings.xml",
        "views/account_payment_method.xml",
        "views/iso20022_code_list.xml",
    ],
    "post_init_hook": "set_default_initiating_party",
    "installable": True,
}
