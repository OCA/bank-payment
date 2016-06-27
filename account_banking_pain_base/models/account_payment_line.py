# -*- coding: utf-8 -*-
# © 2013-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'

    priority = fields.Selection([
        ('NORM', 'Normal'),
        ('HIGH', 'High')],
        string='Priority', default='NORM',
        help="This field will be used as 'Instruction Priority' in "
             "the generated PAIN file.")
    # local_instrument is used in some countries, for example
    # switzerland, cf l10n_ch_sepa that adds some entries in
    # the selection field
    local_instrument = fields.Selection([], string='Local Instrument')
    # PAIN allows 140 characters
    communication = fields.Char(size=140)
    # The field struct_communication_type has been dropped in v9
    # We now use communication_type ; you should add an option
    # in communication_type with selection_add=[]
    communication_type = fields.Selection(selection_add=[('ISO', 'ISO')])
