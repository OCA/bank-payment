# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    # TODO: It doesn't work, I don't understand why
    # So I change the label of the field in the view
    acc_type = fields.Char(string='Bank Account Type')
