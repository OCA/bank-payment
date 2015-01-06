# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#              (C) 2014 Akretion (www.akretion.com)
#
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
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

from openerp import models, fields


class PaymentMode(models.Model):
    _inherit = "payment.mode"

    transfer_account_id = fields.Many2one(
        'account.account', string='Transfer account',
        domain=[('type', '=', 'other'), ('reconcile', '=', True)],
        help='Pay off lines in sent orders with a move on this '
        'account. You can only select accounts of type regular '
        'that are marked for reconciliation')
    transfer_journal_id = fields.Many2one(
        'account.journal', string='Transfer journal',
        help='Journal to write payment entries when confirming '
        'a debit order of this mode')
    transfer_move_option = fields.Selection([
        ('date', 'One move per payment date'),
        ('line', 'One move per payment line'),
        ], string='Transfer move option', default='date')
