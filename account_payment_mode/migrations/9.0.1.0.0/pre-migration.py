# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.addons.account_payment_mode.hooks import migrate_from_8


def migrate(cr, version=None):
    # also support cases where openupgrade renamed the old module
    migrate_from_8(cr)
