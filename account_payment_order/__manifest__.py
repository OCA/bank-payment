# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<https://therp.nl>)
# © 2013-2014 ACSONE SA (<https://acsone.eu>).
# © 2016 Akretion (<https://www.akretion.com>).
# © 2016 Aselcis (<https://www.aselcis.com>).
# © 2014-2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


{
    "name": "Account Payment Order",
    "version": "16.0.1.13.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, "
    "Therp BV, "
    "Tecnativa, "
    "Akretion, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "development_status": "Mature",
    "category": "Banking addons",
    "depends": ["account_payment_partner", "base_iban"],  # for manual_bank_tranfer
    "data": [
        "views/account_payment_method.xml",
        "security/payment_security.xml",
        "security/ir.model.access.csv",
        "wizard/account_payment_line_create_view.xml",
        "wizard/account_invoice_payment_line_multi_view.xml",
        "wizard/account_payment_update_views.xml",
        "views/account_payment_mode.xml",
        "views/account_payment_views.xml",
        "views/account_payment_order.xml",
        "views/account_payment_line.xml",
        "views/account_move_line.xml",
        "views/ir_attachment.xml",
        "views/account_invoice_view.xml",
        "data/payment_seq.xml",
        "report/print_account_payment_order.xml",
        "report/account_payment_order.xml",
        "wizard/res_config_settings.xml",
    ],
    "demo": ["demo/payment_demo.xml"],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
