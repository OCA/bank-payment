# Copyright 2016-2020 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def update_bank_journals(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        ajo = env["account.journal"]
        journals = ajo.search([("type", "=", "bank")])
        sct = env.ref("account_banking_sepa_credit_transfer.sepa_credit_transfer")
        if sct:
            journals.write({"outbound_payment_method_ids": [(4, sct.id)]})
    return
