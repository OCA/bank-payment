# -*- coding: utf-8 -*-
# © 2015-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _
from openerp.exceptions import ValidationError


class ResBank(models.Model):
    _inherit = 'res.bank'

    @api.multi
    @api.constrains('bic')
    def check_bic_length(self):
        for bank in self:
            if bank.bic and len(bank.bic) not in (8, 11):
                raise ValidationError(_(
                    "A valid BIC contains 8 or 11 characters. The BIC '%s' "
                    "contains %d characters, so it is not valid.")
                    % (bank.bic, len(bank.bic)))

# in v9, on res.partner.bank bank_bic is a related of bank_id.bic
