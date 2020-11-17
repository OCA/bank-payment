# Copyright 2020 Compassion Suisse (http://www.compassion.ch)
# @author: David Wulliamoz, Emanuel Cino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, api, _, exceptions


class AccountInvoice(models.Model):

    """ add invoice freeing functionality.
    """
    _inherit = 'account.invoice'

    @api.multi
    def free_payment_lines(self):
        """ finds related payment lines and free them.
        """
        move_line_ids = self.move_id.line_ids.ids
        payment_lines = self.env['account.payment.line'].search([
            ('move_line_id', 'in', move_line_ids)
        ])
        if not payment_lines:
            raise exceptions.UserError(_('No payment line found !'))

        payment_lines.free_line()
