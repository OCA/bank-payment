# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    # I change the label of the field in the view.
    # I would also like to store the field to do easy groupby and search,
    # but it's not possible because the compute method is inherited
    # in base_iban (and maybe in other modules) and, when the field is
    # initially computed+stored, it doesn't take into account the
    # inherits of the method that compute this field
    acc_type = fields.Char(string='Bank Account Type')
