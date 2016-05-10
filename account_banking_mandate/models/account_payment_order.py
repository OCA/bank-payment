# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre - alexis.delattre@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _
from openerp.exceptions import UserError


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    @api.multi
    def draft2open(self):
        for order in self:
            if order.payment_mode_id.payment_method_id.mandate_required:
                for line in order.payment_line_ids:
                    if not line.mandate_id:
                        raise UserError(_(
                            "Missing mandate in payment line %s") % line.name)
        return super(AccountPaymentOrder, self).draft2open()
