# Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
# Copyright (C) 2017 Thinkwell Designs (<http://code.compassfoundation.io>)
# Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Bank Deposit Ticket",
    "category": "Generic Modules/Accounting",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Novapoint Group LLC, "
              "Thinkwell Designs, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "depends": [
        "account_cancel",
    ],
    "data": [
        "data/deposit_method.xml",
        "security/res_groups.xml",
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "views/account_move_line.xml",
        "views/deposit_method.xml",
        "views/deposit_ticket.xml",
        "report/deposit_ticket.xml",
        "report/deposit_ticket_report.xml",
        "wizard/add_deposit_items.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
