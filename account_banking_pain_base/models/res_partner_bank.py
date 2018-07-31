# Copyright 2018 Brain-Tec Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    account_holder = fields.Char(default=' ')

    @api.onchange('partner_id')
    def _onchange_account_holder(self):
        self.account_holder = u'{}'.format(self.partner_id.name)
