# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class BankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    @api.multi
    def button_cancel_reconciliation(self):
        """ Unbind moves that are linked to bank.payment.line
            without cancelling nor deleting them.
        """
        moves_to_unbind = self.env['account.move']
        move_lines_to_unbind = self.env['account.move.line']
        for rec in self:
            for move in rec.journal_entry_ids:
                if any([l.bank_payment_line_id for l in move.line_ids]):
                    moves_to_unbind |= move
                    move_lines_to_unbind |= move.line_ids.filtered(
                        lambda l: l.statement_id == self.statement_id)
        if moves_to_unbind:
            moves_to_unbind.write({'statement_line_id': False})
        if move_lines_to_unbind:
            move_lines_to_unbind.write({'statement_id': False})
        return super(BankStatementLine, self).button_cancel_reconciliation()
