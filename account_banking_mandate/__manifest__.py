# Copyright 2014 Compassion CH - Cyril Sester <csester@compassion.ch>
# Copyright 2014 Tecnativa - Pedro M. Baeza
# Copyright 2015-2020 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2017 Tecnativa - Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Banking Mandate",
    "summary": "Banking mandates",
    "version": "16.0.1.1.0",
    "development_status": "Production/Stable",
    "license": "AGPL-3",
    "author": "Compassion CH, "
    "Tecnativa, "
    "Akretion, "
    "Therp B.V., "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "category": "Banking addons",
    "depends": ["account_payment_order"],
    "data": [
        "views/account_banking_mandate_view.xml",
        "views/account_payment_method.xml",
        "views/account_move_view.xml",
        "views/account_payment_line.xml",
        "views/res_partner_bank_view.xml",
        "views/res_partner.xml",
        "data/mandate_reference_sequence.xml",
        "security/mandate_security.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
