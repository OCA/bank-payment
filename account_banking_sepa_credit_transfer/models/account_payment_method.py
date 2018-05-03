# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import os

class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    pain_version = fields.Selection(selection_add=[
        ('pain.001.001.02', 'pain.001.001.02'),
        ('pain.001.001.03', 'pain.001.001.03 '
         '(recommended for credit transfer)'),
        ('pain.001.001.04', 'pain.001.001.04'),
        ('pain.001.001.05', 'pain.001.001.05'),
        ('pain.001.003.03', 'pain.001.003.03 (credit transfer in Germany)'),
        ])

    @api.multi
    def get_xsd_file_path(self):
        self.ensure_one()
        if self.pain_version in [
                'pain.001.001.02', 'pain.001.001.03', 'pain.001.001.04',
                'pain.001.001.05', 'pain.001.003.03']:
            abs_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) 
            path = '%s/data/%s.xsd'\
                % (abs_path, self.pain_version)
            return path
        return super(AccountPaymentMethod, self).get_xsd_file_path()
