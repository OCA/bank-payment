# -*- coding: utf-8 -*-
# © 2016 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, exceptions, _
from .common import is_sepa_creditor_identifier_valid


class PaymentMode(models.Model):
    _inherit = 'payment.mode'

    sepa_creditor_identifier = fields.Char(
        string='SEPA Creditor Identifier', size=35,
        help="Enter the Creditor Identifier that has been attributed to your "
             "company to make SEPA Direct Debits. If not defined, "
             "SEPA Creditor Identifier from company will be used.\n"
             "This identifier is composed of :\n"
             "- your country ISO code (2 letters)\n"
             "- a 2-digits checkum\n"
             "- a 3-letters business code\n"
             "- a country-specific identifier")

    def _sepa_type_get(self):
        res = super(PaymentMode, self)._sepa_type_get()
        if not res:
            if self.type.code and self.type.code.startswith('pain.008'):
                res = 'sepa_direct_debit'
        return res

    @api.multi
    @api.constrains('sepa_creditor_identifier')
    def _check_sepa_creditor_identifier(self):
        for payment_mode in self:
            if payment_mode.sepa_creditor_identifier:
                if not is_sepa_creditor_identifier_valid(
                        payment_mode.sepa_creditor_identifier):
                    raise exceptions.Warning(
                        _('Error'),
                        _("Invalid SEPA Creditor Identifier."))
