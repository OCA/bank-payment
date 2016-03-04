# -*- coding: utf-8 -*-
# © 2016 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class PaymentMode(models.Model):
    _inherit = 'payment.mode'

    def _sepa_type_get(self):
        res = super(PaymentMode, self)._sepa_type_get()
        if not res:
            if self.type.code and self.type.code.startswith('pain.001'):
                res = 'sepa_credit_transfer'
        return res
