# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos <omar@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, exceptions, _


class PaymentMode(models.Model):

    _inherit = "payment.mode"

    suffix = fields.Char(
        "Suffix", size=3,
        help='Suffix for sepa identifiers with this payment mode. If not set '
             'it will use the company configuration.')

    @api.one
    @api.constrains('suffix')
    def _check_suffix_format(self):
        if self.suffix:
            if len(self.suffix) != 3 or not self.suffix.isdigit():
                raise exceptions.\
                    Warning(_("Suffix must be compound by 3 digits"))
