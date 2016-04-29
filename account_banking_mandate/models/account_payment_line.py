# -*- coding: utf-8 -*-
# © 2014 Compassion CH - Cyril Sester <csester@compassion.ch>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2015-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'

    mandate_id = fields.Many2one(
        comodel_name='account.banking.mandate', string='Direct Debit Mandate',
        domain=[('state', '=', 'valid')])

    # TODO : remove this
    @api.model
    def create(self, vals=None):
        """If the customer invoice has a mandate, take it
        otherwise, take the first valid mandate of the bank account
        """
        if vals is None:
            vals = {}
        partner_bank_id = vals.get('partner_bank_id')
        move_line_id = vals.get('move_line_id')
        if (self.env.context.get('search_payment_order_type') == 'debit' and
                'mandate_id' not in vals):
            if move_line_id:
                line = self.env['account.move.line'].browse(move_line_id)
                if (line.invoice and line.invoice.type == 'out_invoice' and
                        line.invoice.mandate_id):
                    vals.update({
                        'mandate_id': line.invoice.mandate_id.id,
                        'partner_bank_id': line.invoice.mandate_id.partner_bank_id.id,
                    })
            if partner_bank_id and 'mandate_id' not in vals:
                mandates = self.env['account.banking.mandate'].search(
                    [('partner_bank_id', '=', partner_bank_id),
                     ('state', '=', 'valid')])
                if mandates:
                    vals['mandate_id'] = mandates[0].id
        return super(AccountPaymentLine, self).create(vals)

    @api.one
    @api.constrains('mandate_id', 'partner_bank_id')
    def _check_mandate_bank_link(self):
        if (self.mandate_id and self.partner_bank_id and
                self.mandate_id.partner_bank_id.id !=
                self.partner_bank_id.id):
            raise ValidationError(
                _("The payment line with reference '%s' has the bank account "
                  "'%s' which is not attached to the mandate '%s' (this "
                  "mandate is attached to the bank account '%s').") %
                (self.name,
                 self.partner_bank_id.name_get()[0][1],
                 self.mandate_id.unique_mandate_reference,
                 self.mandate_id.partner_bank_id.name_get()[0][1]))

#    @api.multi
#    def check_payment_line(self):
# TODO : i would like to block here is mandate is missing... but how do you know it's required ? => create option on payment order ?
