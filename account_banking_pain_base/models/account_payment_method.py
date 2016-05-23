# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import UserError


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    pain_version = fields.Selection([], string='PAIN Version')
    convert_to_ascii = fields.Boolean(
        string='Convert to ASCII', default=True,
        help="If active, Odoo will convert each accented character to "
        "the corresponding unaccented character, so that only ASCII "
        "characters are used in the generated PAIN file.")

    @api.multi
    def get_xsd_file_path(self):
        """This method is designed to be inherited in the SEPA modules"""
        self.ensure_one()
        raise UserError(_(
            "No XSD file path found for payment method '%s'") % self.name)
