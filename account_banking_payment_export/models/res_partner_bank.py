# -*- coding: utf-8 -*-
# © 2015 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _
from openerp.exceptions import ValidationError


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.multi
    @api.constrains('bank_bic')
    def check_bic_length(self):
        for pbank in self:
            if pbank.bank_bic and len(pbank.bank_bic) not in (8, 11):
                raise ValidationError(_(
                    "A valid BIC contains 8 or 11 caracters. The BIC '%s' "
                    "contains %d caracters, so it is not valid.")
                    % (pbank.bank_bic, len(pbank.bank_bic)))


class ResBank(models.Model):
    _inherit = 'res.bank'

    @api.multi
    @api.constrains('bic')
    def check_bic_length(self):
        for bank in self:
            if bank.bic and len(bank.bic) not in (8, 11):
                raise ValidationError(_(
                    "A valid BIC contains 8 or 11 caracters. The BIC '%s' "
                    "contains %d caracters, so it is not valid.")
                    % (bank.bic, len(bank.bic)))
