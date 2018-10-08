# Copyright 2018 Brain-Tec Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    account_holder = fields.Char(default=' ',
                                 help='Fill this field if the account'
                                      ' holder\'s name differ from the'
                                      ' partner name')
