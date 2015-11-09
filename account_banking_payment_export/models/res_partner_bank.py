# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
