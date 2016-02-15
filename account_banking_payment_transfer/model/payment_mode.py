# -*- coding: utf-8 -*-
# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<http://therp.nl>)
# © 2014 Akretion (www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
