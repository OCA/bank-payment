# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) ACSONE SA/NV (<http://acsone.eu>).
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

from openerp import models, fields


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    bank = fields.Many2one(help="If this field is set and the related bank "
                                "has a 'Bank Identifier Code', then this BIC "
                                "will be used to generate the credit "
                                "transfers and direct debits files.")
    bank_bic = fields.Char(help="In the generation of credit transfer and "
                                "direct debit files, this BIC will be used "
                                "only when the 'Bank' field is empty, or "
                                "has a value but the field 'Bank Identifier "
                                "Code' is not set on the related bank.")
