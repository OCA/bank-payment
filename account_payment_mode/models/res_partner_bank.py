# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    # I also have to change the label of the field in the view
    # I store the field, so that we can do groupby and search on it
    acc_type = fields.Char(string='Bank Account Type', store=True)
