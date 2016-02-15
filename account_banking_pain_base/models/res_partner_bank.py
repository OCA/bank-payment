# -*- coding: utf-8 -*-
# © 2013 ACSONE SA/NV (<http://acsone.eu>)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
