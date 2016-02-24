# -*- coding: utf-8 -*-
# © 2013-2014 ACSONE SA (<http://acsone.eu>).
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _get_reference_type(self):
        rt = super(AccountInvoice, self)._get_reference_type()
        rt.append(('structured', _('Structured Reference')))
        return rt
