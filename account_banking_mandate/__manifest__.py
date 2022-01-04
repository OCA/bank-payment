# Copyright 2014-2022 Compassion CH - Cyril Sester <csester@compassion.ch>
# Copyright 2014-2022 Tecnativa - Pedro M. Baeza
# Copyright 2015-2022 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2017-2022 Tecnativa - Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Banking Mandate",
    "summary": "Banking mandates",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "Compassion CH, "
    "Tecnativa, "
    "Akretion, "
    "Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/bank-payment",
    "category": "Banking addons",
    "depends": ["account_payment_order"],
    "data": [
        "views/account_banking_mandate.xml",
        "views/account_payment_method.xml",
        "views/account_move.xml",
        "views/account_payment_line.xml",
        "views/res_partner_bank.xml",
        "views/res_partner.xml",
        "views/bank_payment_line.xml",
        "data/mandate_reference_sequence.xml",
        "security/mandate_security.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
