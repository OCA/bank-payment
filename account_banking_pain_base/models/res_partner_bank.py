# Copyright 2018 Brain-Tec Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    account_holder = fields.Char(default=' ',
                                 help='Fill this field if the account'
                                      ' holder\'s name differ from the'
                                      ' partner name')

    @api.onchange('partner_id')
    def _onchange_partner_id_account_banking_pain_base(self):
        self.account_holder = u'{}'.format(self.partner_id.name)
