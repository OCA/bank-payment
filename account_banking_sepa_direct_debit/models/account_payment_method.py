# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    pain_version = fields.Selection(selection_add=[
        ('pain.008.001.02', 'pain.008.001.02 (recommended for direct debit)'),
        ('pain.008.001.03', 'pain.008.001.03'),
        ('pain.008.001.04', 'pain.008.001.04'),
        ('pain.008.003.02', 'pain.008.003.02 (direct debit in Germany)'),
        ])

    @api.multi
    def get_xsd_file_path(self):
        self.ensure_one()
        if self.pain_version in [
                'pain.008.001.02', 'pain.008.001.03', 'pain.008.001.04',
                'pain.008.003.02']:
            path = 'account_banking_sepa_direct_debit/data/%s.xsd'\
                % self.pain_version
            return path
        return super(AccountPaymentMethod, self).get_xsd_file_path()
