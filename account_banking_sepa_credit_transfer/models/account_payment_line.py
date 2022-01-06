# -*- coding: utf-8 -*-
# © 2017 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'

    # local_instrument 'INST' used for instant credit transfers
    # which will begin on November 21st 2017, cf
    # https://www.europeanpaymentscouncil.eu/document-library/
    # rulebooks/2017-sepa-instant-credit-transfer-rulebook
    local_instrument = fields.Selection(
        selection_add=[('INST', 'Instant Transfer')])
