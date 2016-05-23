# -*- coding: utf-8 -*-
# © 2014 Compassion CH - Cyril Sester <csester@compassion.ch>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    mandate_ids = fields.One2many(
        comodel_name='account.banking.mandate', inverse_name='partner_bank_id',
        string='Direct Debit Mandates',
        help='Banking mandates represent an authorization that the bank '
             'account owner gives to a company for a specific operation.')
