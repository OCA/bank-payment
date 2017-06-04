# -*- encoding: utf-8 -*-
###############################################################################
# Copyright 2015 Roberto Lizana
# For license notices, see __openerp__.py file in root directory
###############################################################################
from openerp import models, api, exceptions, _


class PaymentOrder(models.Model):
    _inherit = 'payment.order'

    @api.one
    def action_cancel(self):
        lines = [
            '%s - %s' % (l.communication, l.partner_id.display_name)
            for l in self.line_ids
            if l.move_line_id.reconcile_id
            or l.move_line_id.reconcile_partial_id]
        if lines:
            raise exceptions.Warning(
                _('You cannot cancel, the next lines has already been '
                  'reconciled: \n%s\n') % '\n'.join(lines))
