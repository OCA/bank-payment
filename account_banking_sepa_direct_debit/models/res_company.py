# -*- coding: utf-8 -*-
# © 2013 Akretion (www.akretion.com)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, exceptions, _
import logging

logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    sepa_creditor_identifier = fields.Char(
        string='SEPA Creditor Identifier', size=35,
        help="Enter the Creditor Identifier that has been attributed to your "
             "company to make SEPA Direct Debits. This identifier is composed "
             "of :\n- your country ISO code (2 letters)\n- a 2-digits "
             "checkum\n- a 3-letters business code\n- a country-specific "
             "identifier")
    original_creditor_identifier = fields.Char(
        string='Original Creditor Identifier', size=70)

    def is_sepa_creditor_identifier_valid(
            self, sepa_creditor_identifier):
        """Check if SEPA Creditor Identifier is valid
        @param sepa_creditor_identifier: SEPA Creditor Identifier as str
            or unicode
        @return: True if valid, False otherwise
        """
        if not isinstance(sepa_creditor_identifier, (str, unicode)):
            return False
        try:
            sci = str(sepa_creditor_identifier).lower()
        except:
            logger.warning(
                "SEPA Creditor ID should contain only ASCII caracters.")
            return False
        if len(sci) < 9:
            return False
        before_replacement = sci[7:] + sci[0:2] + '00'
        logger.debug(
            "SEPA ID check before_replacement = %s" % before_replacement)
        after_replacement = ''
        for char in before_replacement:
            if char.isalpha():
                after_replacement += str(ord(char) - 87)
            else:
                after_replacement += char
        logger.debug(
            "SEPA ID check after_replacement = %s" % after_replacement)
        return int(sci[2:4]) == (98 - (int(after_replacement) % 97))

    @api.one
    @api.constrains('sepa_creditor_identifier')
    def _check_sepa_creditor_identifier(self):
        if self.sepa_creditor_identifier:
            if not self.is_sepa_creditor_identifier_valid(
                    self.sepa_creditor_identifier):
                raise exceptions.Warning(
                    _('Error'),
                    _("Invalid SEPA Creditor Identifier."))
