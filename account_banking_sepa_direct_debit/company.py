# -*- encoding: utf-8 -*-
##############################################################################
#
#    SEPA Direct Debit module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp.osv import orm, fields
import logging

logger = logging.getLogger(__name__)


class res_company(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'sepa_creditor_identifier': fields.char(
            'SEPA Creditor Identifier', size=35,
            help="Enter the Creditor Identifier that has been attributed "
            "to your company to make SEPA Direct Debits. This identifier "
            "is composed of :\n- your country ISO code (2 letters)\n- a "
            "2-digits checkum\n- a 3-letters business code\n- a "
            "country-specific identifier"),
        'original_creditor_identifier': fields.char(
            'Original Creditor Identifier', size=70),
    }

    def is_sepa_creditor_identifier_valid(
            self, cr, uid, sepa_creditor_identifier, context=None):
        """Check if SEPA Creditor Identifier is valid
        @param sepa_creditor_identifier: SEPA Creditor Identifier as str
            or unicode
        @return: True if valid, False otherwise
        """
        if not isinstance(sepa_creditor_identifier, (str, unicode)):
            return False
        try:
            sci_str = str(sepa_creditor_identifier)
        except:
            logger.warning(
                "SEPA Creditor ID should contain only ASCII caracters.")
            return False
        sci = sci_str.lower()
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
        if int(sci[2:4]) == (98 - (int(after_replacement) % 97)):
            return True
        else:
            return False

    def _check_sepa_creditor_identifier(self, cr, uid, ids):
        for company in self.browse(cr, uid, ids):
            if company.sepa_creditor_identifier:
                if not self.is_sepa_creditor_identifier_valid(
                        cr, uid, company.sepa_creditor_identifier):
                    return False
        return True

    _constraints = [
        (_check_sepa_creditor_identifier,
            "Invalid SEPA Creditor Identifier.",
            ['sepa_creditor_identifier']),
    ]
