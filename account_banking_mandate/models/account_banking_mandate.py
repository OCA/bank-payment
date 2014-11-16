# -*- encoding: utf-8 -*-
##############################################################################
#
#    Mandate module for openERP
#    Copyright (C) 2014 Compassion CH (http://www.compassion.ch)
#    @author: Cyril Sester <csester@compassion.ch>,
#             Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp import models, fields, exceptions, api, _


class AccountBankingMandate(models.Model):
    ''' The banking mandate is attached to a bank account and represents an
        authorization that the bank account owner gives to a company for a
        specific operation (such as direct debit)
    '''
    _name = 'account.banking.mandate'
    _description = "A generic banking mandate"
    _rec_name = 'unique_mandate_reference'
    _inherit = ['mail.thread']
    _order = 'signature_date desc'
    _track = {
        'state': {
            'account_banking_mandate.mandate_valid': (
                lambda self, cr, uid, obj, ctx=None: obj['state'] == 'valid'),
            'account_banking_mandate.mandate_expired': (
                lambda self, cr, uid, obj, ctx=None:
                obj['state'] == 'expired'),
            'account_banking_mandate.mandate_cancel': (
                lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel'),
        },
    }

    def _get_states(self):
        return [('draft', 'Draft'),
                ('valid', 'Valid'),
                ('expired', 'Expired'),
                ('cancel', 'Cancelled')]

    partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank', string='Bank Account',
        track_visibility='onchange')
    partner_id = fields.Many2one(
        comodel_name='res.partner', related='partner_bank_id.partner_id',
        string='Partner', store=True)
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'account.banking.mandate'))
    unique_mandate_reference = fields.Char(
        string='Unique Mandate Reference', track_visibility='always',
        default='/')
    signature_date = fields.Date(string='Date of Signature of the Mandate',
                                 track_visibility='onchange')
    scan = fields.Binary(string='Scan of the Mandate')
    last_debit_date = fields.Date(string='Date of the Last Debit',
                                  readonly=True)
    state = fields.Selection(
        _get_states, string='Status', default='draft',
        help="Only valid mandates can be used in a payment line. A cancelled "
             "mandate is a mandate that has been cancelled by the customer.")
    payment_line_ids = fields.One2many(
        comodel_name='payment.line', inverse_name='mandate_id',
        string="Related Payment Lines")

    _sql_constraints = [(
        'mandate_ref_company_uniq',
        'unique(unique_mandate_reference, company_id)',
        'A Mandate with the same reference already exists for this company !')]

    @api.one
    @api.constrains('signature_date', 'last_debit_date')
    def _check_dates(self):
        if (self.signature_date and
                self.signature_date > fields.Date.context_today(self)):
            raise exceptions.Warning(
                _("The date of signature of mandate '%s' is in the future !")
                % self.unique_mandate_reference)
        if (self.signature_date and self.last_debit_date and
                self.signature_date > self.last_debit_date):
            raise exceptions.Warning(
                _("The mandate '%s' can't have a date of last debit before "
                  "the date of signature.") % self.unique_mandate_reference)

    @api.one
    @api.constrains('state', 'partner_bank_id')
    def _check_valid_state(self):
        if self.state == 'valid':
            if not self.signature_date:
                raise exceptions.Warning(
                    _("Cannot validate the mandate '%s' without a date of "
                      "signature.") % self.unique_mandate_reference)
            if not self.partner_bank_id:
                raise exceptions.Warning(
                    _("Cannot validate the mandate '%s' because it is not "
                      "attached to a bank account.") %
                    self.unique_mandate_reference)

    @api.model
    def create(self, vals=None):
        if vals.get('unique_mandate_reference', '/') == '/':
            vals['unique_mandate_reference'] = \
                self.env['ir.sequence'].next_by_code('account.banking.mandate')
        return super(AccountBankingMandate, self).create(vals)

    @api.one
    @api.onchange('partner_bank_id')
    def mandate_partner_bank_change(self):
        self.partner_id = self.partner_bank_id.partner_id

    @api.multi
    def validate(self):
        for mandate in self:
            if mandate.state != 'draft':
                raise exceptions.Warning(
                    _('Mandate should be in draft state'))
        self.write({'state': 'valid'})
        return True

    @api.multi
    def cancel(self):
        for mandate in self:
            if mandate.state not in ('draft', 'valid'):
                raise exceptions.Warning(
                    _('Mandate should be in draft or valid state'))
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def back2draft(self):
        """Allows to set the mandate back to the draft state.
        This is for mandates cancelled by mistake.
        """
        for mandate in self:
            if mandate.state != 'cancel':
                raise exceptions.Warning(
                    _('Mandate should be in cancel state'))
        self.write({'state': 'draft'})
        return True
