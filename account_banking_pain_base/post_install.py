# -*- coding: utf-8 -*-
# © 2015 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import SUPERUSER_ID


def set_default_initiating_party(cr, pool):
    company_ids = pool['res.company'].search(cr, SUPERUSER_ID, [])
    companies = pool['res.company'].browse(cr, SUPERUSER_ID, company_ids)
    for company in companies:
        pool['res.company']._default_initiating_party(
            cr, SUPERUSER_ID, company)
    return
