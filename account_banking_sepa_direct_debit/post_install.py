# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID


def update_bank_journals(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        ajo = env['account.journal']
        journals = ajo.search([('type', '=', 'bank')])
        sdd = env.ref(
            'account_banking_sepa_direct_debit.sepa_direct_debit')
        if sdd:
            journals.write({
                'inbound_payment_method_ids': [(4, sdd.id)],
            })
    return
