# -*- coding: utf-8 -*-
# © 2015 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.account_banking_pain_base.post_install\
    import set_default_initiating_party
from openerp import pooler


def migrate(cr, version):
    if not version:
        return

    pool = pooler.get_pool(cr.dbname)
    set_default_initiating_party(cr, pool)
