# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.tools import float_is_zero


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # TODO Should we keep this field ?
#    journal_entry_ref = fields.Char(compute='_get_journal_entry_ref',
#                                    string='Journal Entry Ref')
    partner_bank_id = fields.Many2one(
        'res.partner.bank', string='Partner Bank Account',
        help='Bank account on which we should pay the supplier')

#    @api.one
#    def _get_journal_entry_ref(self):
#        if self.move_id.state == 'draft':
#            if self.invoice.id:
#                self.journal_entry_ref = self.invoice.number
#            else:
#                self.journal_entry_ref = '*' + str(self.move_id.id)
#        else:
#            self.journal_entry_ref = self.move_id.name

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

    @api.multi
    def _prepare_payment_line_vals(self, payment_order):
        self.ensure_one()
        assert payment_order, 'Missing payment order'
        aplo = self.env['account.payment.line']
        # default values for communication_type and communication
        communication_type = 'normal'
        communication = self.move_id.name or '-'
        # change these default values if move line is linked to an invoice
        if self.invoice_id:
            if self.invoice_id.reference_type != 'none':
                communication = self.invoice_id.reference
                ref2comm_type =\
                    aplo.invoice_reference_type2communication_type()
                communication_type =\
                    ref2comm_type[self.invoice_id.reference_type]
            else:
                if (
                        self.invoice_id.type in ('in_invoice', 'in_refund')
                        and self.invoice_id.reference):
                    communication = self.invoice_id.reference
        if self.currency_id:
            currency_id = self.currency_id.id
            amount_currency = self.amount_residual_currency
        else:
            currency_id = self.company_id.currency_id.id
            amount_currency = self.amount_residual
            # TODO : check that self.amount_residual_currency is 0 in this case
        precision = self.env['decimal.precision'].precision_get('Account')
        if payment_order.payment_type == 'outbound':
            amount_currency *= -1
        vals = {
            'order_id': payment_order.id,
            'partner_bank_id': self.partner_bank_id.id,
            'partner_id': self.partner_id.id,
            'move_line_id': self.id,
            'communication': communication,
            'communication_type': communication_type,
            'currency_id': currency_id,
            'amount_currency': amount_currency,
            # date is set when the user confirms the payment order
            }
        return vals

    @api.multi
    def create_payment_line_from_move_line(self, payment_order):
        aplo = self.env['account.payment.line']
        for mline in self:
            aplo.create(mline._prepare_payment_line_vals(payment_order))
        return
