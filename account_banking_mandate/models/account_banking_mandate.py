# Copyright 2014 Compassion CH - Cyril Sester <csester@compassion.ch>
# Copyright 2014 Tecnativa - Pedro M. Baeza
# Copyright 2015-16 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountBankingMandate(models.Model):
    """The banking mandate is attached to a bank account and represents an
    authorization that the bank account owner gives to a company for a
    specific operation (such as direct debit)
    """
    _name = 'account.banking.mandate'
    _description = "A generic banking mandate"
    _rec_name = 'unique_mandate_reference'
    _inherit = ['mail.thread']
    _order = 'signature_date desc'

    def _get_default_partner_bank_id_domain(self):
        if 'default_partner_id' in self.env.context:
            return [('partner_id', '=', self.env.context.get(
                'default_partner_id'))]
        else:
            return []

    format = fields.Selection(
        [('basic', 'Basic Mandate')], default='basic', required=True,
        string='Mandate Format', track_visibility='onchange')
    type = fields.Selection(
        [('generic', 'Generic Mandate')],
        string='Type of Mandate',
        track_visibility='onchange'
    )
    partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank', string='Bank Account',
        track_visibility='onchange',
        domain=lambda self: self._get_default_partner_bank_id_domain(),
        ondelete='restrict',
        index=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner', related='partner_bank_id.partner_id',
        string='Partner', store=True, index=True)
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'account.banking.mandate'))
    unique_mandate_reference = fields.Char(
        string='Unique Mandate Reference', track_visibility='onchange',
        copy=False,
    )
    signature_date = fields.Date(string='Date of Signature of the Mandate',
                                 track_visibility='onchange')
    scan = fields.Binary(string='Scan of the Mandate')
    last_debit_date = fields.Date(string='Date of the Last Debit',
                                  readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('cancel', 'Cancelled'),
        ], string='Status', default='draft', track_visibility='onchange',
        help="Only valid mandates can be used in a payment line. A cancelled "
        "mandate is a mandate that has been cancelled by the customer.")
    payment_line_ids = fields.One2many(
        comodel_name='account.payment.line', inverse_name='mandate_id',
        string="Related Payment Lines")
    payment_line_ids_count = fields.Integer(
        compute='_compute_payment_line_ids_count',
    )

    _sql_constraints = [(
        'mandate_ref_company_uniq',
        'unique(unique_mandate_reference, company_id)',
        'A Mandate with the same reference already exists for this company!')]

    @api.multi
    @api.depends('payment_line_ids')
    def _compute_payment_line_ids_count(self):
        payment_line_model = self.env['account.payment.line']
        domain = [('mandate_id', 'in', self.ids)]
        res = payment_line_model.read_group(
            domain=domain,
            fields=['mandate_id'],
            groupby=['mandate_id'],
        )
        payment_line_dict = {}
        for dic in res:
            mandate_id = dic['mandate_id'][0]
            payment_line_dict.setdefault(mandate_id, 0)
            payment_line_dict[mandate_id] += dic['mandate_id_count']
        for rec in self:
            rec.payment_line_ids_count = payment_line_dict.get(rec.id, 0)

    @api.multi
    def show_payment_lines(self):
        self.ensure_one()
        return {
            'name': _("Payment lines"),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.payment.line',
            'domain': [('mandate_id', '=', self.id)],
        }

    @api.multi
    @api.constrains('signature_date', 'last_debit_date')
    def _check_dates(self):
        for mandate in self:
            if (mandate.signature_date and
                    mandate.signature_date > fields.Date.context_today(
                        mandate)):
                raise ValidationError(
                    _("The date of signature of mandate '%s' "
                      "is in the future!")
                    % mandate.unique_mandate_reference)
            if (mandate.signature_date and mandate.last_debit_date and
                    mandate.signature_date > mandate.last_debit_date):
                raise ValidationError(
                    _("The mandate '%s' can't have a date of last debit "
                      "before the date of signature."
                      ) % mandate.unique_mandate_reference)

    @api.constrains('company_id', 'payment_line_ids', 'partner_bank_id')
    def _company_constrains(self):
        for mandate in self:
            if mandate.partner_bank_id.company_id and \
                    mandate.partner_bank_id.company_id != mandate.company_id:
                raise ValidationError(
                    _("The company of the mandate %s differs from the "
                      "company of partner %s.") %
                    (mandate.display_name, mandate.partner_id.name))

            if self.env['account.payment.line'].sudo().search(
                    [('mandate_id', '=', mandate.id),
                     ('company_id', '!=', mandate.company_id.id)], limit=1):
                raise ValidationError(
                    _("You cannot change the company of mandate %s, "
                      "as there exists payment lines referencing it that "
                      "belong to another company.") %
                    (mandate.display_name, ))

            if self.env['account.invoice'].sudo().search(
                    [('mandate_id', '=', mandate.id),
                     ('company_id', '!=', mandate.company_id.id)], limit=1):
                raise ValidationError(
                    _("You cannot change the company of mandate %s, "
                      "as there exists invoices referencing it that belong to "
                      "another company.") %
                    (mandate.display_name, ))

            if self.env['account.move.line'].sudo().search(
                    [('mandate_id', '=', mandate.id),
                     ('company_id', '!=', mandate.company_id.id)], limit=1):
                raise ValidationError(
                    _("You cannot change the company of mandate %s, "
                      "as there exists journal items referencing it that "
                      "belong to another company.") %
                    (mandate.display_name, ))

            if self.env['bank.payment.line'].sudo().search(
                    [('mandate_id', '=', mandate.id),
                     ('company_id', '!=', mandate.company_id.id)], limit=1):
                raise ValidationError(
                    _("You cannot change the company of mandate %s, "
                      "as there exists bank payment lines referencing it that "
                      "belong to another company.") %
                    (mandate.display_name, ))

    @api.multi
    @api.constrains('state', 'partner_bank_id', 'signature_date')
    def _check_valid_state(self):
        for mandate in self:
            if mandate.state == 'valid':
                if not mandate.signature_date:
                    raise ValidationError(
                        _("Cannot validate the mandate '%s' without a date of "
                          "signature.") % mandate.unique_mandate_reference)
                if not mandate.partner_bank_id:
                    raise ValidationError(
                        _("Cannot validate the mandate '%s' because it is not "
                          "attached to a bank account.") %
                        mandate.unique_mandate_reference)

    @api.model
    def create(self, vals=None):
        unique_mandate_reference = vals.get('unique_mandate_reference')
        if not unique_mandate_reference or unique_mandate_reference == 'New':
            vals['unique_mandate_reference'] = \
                self.env['ir.sequence'].next_by_code(
                    'account.banking.mandate') or 'New'
        return super(AccountBankingMandate, self).create(vals)

    @api.multi
    @api.onchange('partner_bank_id')
    def mandate_partner_bank_change(self):
        for mandate in self:
            mandate.partner_id = mandate.partner_bank_id.partner_id

    @api.multi
    def validate(self):
        for mandate in self:
            if mandate.state != 'draft':
                raise UserError(
                    _('Mandate should be in draft state.'))
        self.write({'state': 'valid'})
        return True

    @api.multi
    def cancel(self):
        for mandate in self:
            if mandate.state not in ('draft', 'valid'):
                raise UserError(
                    _('Mandate should be in draft or valid state.'))
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def back2draft(self):
        """Allows to set the mandate back to the draft state.
        This is for mandates cancelled by mistake.
        """
        for mandate in self:
            if mandate.state != 'cancel':
                raise UserError(
                    _('Mandate should be in cancel state.'))
        self.write({'state': 'draft'})
        return True
