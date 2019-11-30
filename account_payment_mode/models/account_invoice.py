# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.tools import config


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_default_bank_id(self, type, company_id):
        """When OCA payment mode is used we don't want default bank acc"""
        context = self.env.context
        if config['test_enable'] and not context.get(
            'test_account_payment_mode') or context.get(
                'force_std_default_bank_id'):
            return super()._get_default_bank_id(type, company_id)
        else:
            return False
