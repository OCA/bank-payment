# -*- coding: utf-8 -*-
# © 2004-2014 OpenERP S.A. (http://www.openerp.com/)
# © 2014 Akretion (http://www.akretion.com/)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.one
    def _get_journal_entry_ref(self):
        if self.move_id.state == 'draft':
            if self.invoice.id:
                self.journal_entry_ref = self.invoice.number
            else:
                self.journal_entry_ref = '*' + str(self.move_id.id)
        else:
            self.journal_entry_ref = self.move_id.name

    journal_entry_ref = fields.Char(compute=_get_journal_entry_ref,
                                    string='Journal Entry Ref')

    @api.multi
    def get_balance(self):
        """
        Return the balance of any set of move lines.

        Not to be confused with the 'balance' field on this model, which
        returns the account balance that the move line applies to.
        """
        total = 0.0
        for line in self:
            total += (line.debit or 0.0) - (line.credit or 0.0)
        return total
