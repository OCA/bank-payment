# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Vincent Renaville (Camptocamp)
#    Copyright 2015 Camptocamp SA
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
from openerp import models, fields, api, exceptions, _


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    currency_symbol = fields.Char(
        string='Journal Currency',
        related='statement_id.currency.symbol',
        related_sudo=False, readonly=True)


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.multi
    def check_line_amount_zero(self):
        self.ensure_one()
        msg = ''
        for line in self.line_ids:
            if not line.amount:
                msg += _('Amount on line %s is not set. \n') % (line.name)
        if msg:
            raise exceptions.Warning(
                _("Error on bank statement: \n %s") % msg)
        # dispatch to reconciliation interface
        action = self.env.ref(
            'account.action_bank_reconcile_bank_statements')
        return {
            'name': action.name,
            'tag': action.tag,
            'context': {
                'statement_ids': self.ids,
            },
            'type': 'ir.actions.client',
        }
