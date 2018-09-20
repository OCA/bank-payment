# © 2015-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, SUPERUSER_ID
import logging

logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    logger.info('Launching the post init hook')
    cr.execute("""
        UPDATE res_partner_bank SET account_holder =
        (SELECT name FROM res_partner WHERE res_partner.id =
        res_partner_bank.partner_id);
        """)
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        for company in env['res.company'].search([]):
            company._default_initiating_party()
    return
