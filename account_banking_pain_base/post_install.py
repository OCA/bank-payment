# © 2015-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import SUPERUSER_ID, api


def set_default_initiating_party(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        for company in env["res.company"].search([]):
            company._default_initiating_party()
    return
