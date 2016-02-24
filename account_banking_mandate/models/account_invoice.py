# -*- coding: utf-8 -*-
# © 2014 Compassion CH - Cyril Sester <csester@compassion.ch>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    mandate_id = fields.Many2one(
        'account.banking.mandate', string='Direct Debit Mandate',
        domain=[('state', '=', 'valid')], readonly=True,
        states={'draft': [('readonly', False)]})
