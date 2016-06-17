# -*- coding: utf-8 -*-
# © 2013 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, exceptions, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

NUMBER_OF_UNUSED_MONTHS_BEFORE_EXPIRY = 36

logger = logging.getLogger(__name__)


class AccountBankingMandate(models.Model):
    """SEPA Direct Debit Mandate"""
    _inherit = 'account.banking.mandate'
    _track = {
        'recurrent_sequence_type': {
            'account_banking_sepa_direct_debit.recurrent_sequence_type_first':
            lambda self, cr, uid, obj, ctx=None:
            obj['recurrent_sequence_type'] == 'first',
            'account_banking_sepa_direct_debit.'
            'recurrent_sequence_type_recurring':
            lambda self, cr, uid, obj, ctx=None:
            obj['recurrent_sequence_type'] == 'recurring',
            'account_banking_sepa_direct_debit.recurrent_sequence_type_final':
            lambda self, cr, uid, obj, ctx=None:
            obj['recurrent_sequence_type'] == 'final',
        }
    }

    format = fields.Selection(
        selection_add=[('sepa', _('Sepa Mandate'))],
        default='sepa',
    )
    type = fields.Selection([('recurrent', 'Recurrent'),
                             ('oneoff', 'One-Off')],
                            string='Type of Mandate',
                            track_visibility='always')
    recurrent_sequence_type = fields.Selection(
        [('first', 'First'),
         ('recurring', 'Recurring'),
         ('final', 'Final')],
        string='Sequence Type for Next Debit', track_visibility='onchange',
        help="This field is only used for Recurrent mandates, not for "
             "One-Off mandates.", default="first")
    sepa_migrated = fields.Boolean(
        string='Migrated to SEPA', track_visibility='onchange',
        help="If this field is not active, the mandate section of the next "
             "direct debit file that include this mandate will contain the "
             "'Original Mandate Identification' and the 'Original Creditor "
             "Scheme Identification'. This is required in a few countries "
             "(Belgium for instance), but not in all countries. If this is "
             "not required in your country, you should keep this field always "
             "active.", default=True)
    original_mandate_identification = fields.Char(
        string='Original Mandate Identification', track_visibility='onchange',
        size=35,
        help="When the field 'Migrated to SEPA' is not active, this field "
             "will be used as the Original Mandate Identification in the "
             "Direct Debit file.")
    scheme = fields.Selection([('CORE', 'Basic (CORE)'),
                               ('B2B', 'Enterprise (B2B)')],
                              string='Scheme', default="CORE")
    unique_mandate_reference = fields.Char(size=35)  # cf ISO 20022
    amendment_state = fields.Selection(
        [('next', 'At next debit order'),
         ('sent', 'Sent in last debit order')])
    amendment_type = fields.Selection(
        [('account', 'Change of customer bank account')])
    original_debtor_account = fields.Char(
        string="Previous customer bank account number",
        help=("If the new bank account of this mandate is at the same bank, "
              "this field should contain the old bank account number, and the "
              "BIC below should be left empty."))
    original_debtor_agent = fields.Char(
        string="Previous customer bank's BIC",
        help=("If the new bank account of this mandate is not at the same "
              "bank, this field should contain the old bank's BIC. In that "
              "case, the original bank account number is just for reference "
              "purposes and is not included in the amendment."))

    @api.multi
    @api.constrains('type', 'recurrent_sequence_type')
    def _check_recurring_type(self):
        for mandate in self:
            if (mandate.type == 'recurrent' and
                    not mandate.recurrent_sequence_type):
                raise exceptions.Warning(
                    _("The recurrent mandate '%s' must have a sequence type.")
                    % mandate.unique_mandate_reference)

    @api.multi
    @api.constrains('type', 'recurrent_sequence_type', 'sepa_migrated')
    def _check_migrated_to_sepa(self):
        for mandate in self:
            if (mandate.type == 'recurrent' and not mandate.sepa_migrated and
                    mandate.recurrent_sequence_type != 'first'):
                raise exceptions.Warning(
                    _("The recurrent mandate '%s' which is not marked as "
                      "'Migrated to SEPA' must have its recurrent sequence "
                      "type set to 'First'.")
                    % mandate.unique_mandate_reference)

    @api.multi
    @api.constrains('type', 'original_mandate_identification', 'sepa_migrated')
    def _check_original_mandate_identification(self):
        for mandate in self:
            if (mandate.type == 'recurrent' and not mandate.sepa_migrated and
                    not mandate.original_mandate_identification):
                raise exceptions.Warning(
                    _("You must set the 'Original Mandate Identification' on "
                      "the recurrent mandate '%s' which is not marked as "
                      "'Migrated to SEPA'.")
                    % mandate.unique_mandate_reference)

    @api.multi
    @api.constrains('amendment_type', 'original_debtor_account',
                    'original_debtor_agent')
    def _check_amendment(self):
        for mandate in self:
            if (mandate.amendment_type == 'account' and
                not (mandate.original_debtor_account or
                     mandate.original_debtor_agent)):
                raise exceptions.Warning(
                    _("Mandate '%s' has an amendment of type 'account' and "
                      "must contain the original account number or original "
                      "BIC.") % mandate.unique_mandate_reference)

    @api.multi
    @api.onchange('partner_bank_id')
    def mandate_partner_bank_change(self):
        for mandate in self:
            super(AccountBankingMandate, self).mandate_partner_bank_change()
            res = {}
            if (mandate.state == 'valid' and
                    mandate.partner_bank_id and
                    mandate.type == 'recurrent' and
                    mandate.recurrent_sequence_type != 'first'):
                res['warning'] = {
                    'title': _('Mandate update'),
                    'message': _("As you changed the bank account attached "
                                 "to this mandate, the mandate info will be "
                                 "updated when you save it."),
                }
            return res

    @api.model
    def _sdd_mandate_set_state_to_expired(self):
        logger.info('Searching for SDD Mandates that must be set to Expired')
        expire_limit_date = datetime.today() + \
            relativedelta(months=-NUMBER_OF_UNUSED_MONTHS_BEFORE_EXPIRY)
        expire_limit_date_str = expire_limit_date.strftime('%Y-%m-%d')
        expired_mandates = self.search(
            ['|',
             ('last_debit_date', '=', False),
             ('last_debit_date', '<=', expire_limit_date_str),
             ('state', '=', 'valid'),
             ('signature_date', '<=', expire_limit_date_str)])
        if expired_mandates:
            expired_mandates.write({'state': 'expired'})
            logger.info(
                'The following SDD Mandate IDs has been set to expired: %s'
                % expired_mandates.ids)
        else:
            logger.info('0 SDD Mandates must be set to Expired')
        return True

    @api.multi
    def amendment_sent(self):
        """ If amendments are in state 'next', put forward to state 'sent'. For
        amendments that were already in this state, assume that the amendment
        was sent in the previous order and that no rejection has taken place.
        In that case, clear the amendment. """
        self.filtered(lambda md: md.amendment_state == 'sent').write({
            'amendment_state': False,
            'amendment_type': False,
            'original_debtor_account': False,
            'original_debtor_agent': False
        })
        self.filtered(lambda md: md.amendment_state == 'next').write(
            {'amendment_state': 'sent'})

    @api.multi
    def amendment_reset(self):
        """ A rejection has taken place. Set pending amendments back to next
        and reset mandate to FRST if this is a different financial institution
        """
        self.filtered(lambda md: md.amendment_state == 'sent').write(
            {'amendment_state': 'next'})
        self.filtered(lambda md: md.amendment_state == 'next' and
                      md.amendment_type == 'account' and
                      md.original_debtor_agent).write(
                          {'recurrent_sequence_type': 'first'})

    @api.model
    def get_amendment_vals(self, old_bank, new_bank):
        vals = {
            'amendment_state': 'next',
            'amendment_type': 'account',
            'original_debtor_account': old_bank.acc_number,
        }
        new_bic = new_bank.bank_bic or new_bank.bank.bic
        old_bic = old_bank.bank_bic or old_bank.bank.bic
        if new_bic and old_bic and new_bic != old_bic:
            vals.update({
                'original_debtor_agent': old_bic,
                'recurrent_sequence_type': 'first',
            })
        return vals

    @api.multi
    def write(self, vals):
        """ Inject amendment vals if the bank account changes """
        if (vals.get('partner_bank_id') and len(self) == 1 and
                self.partner_bank_id and self.state == 'valid' and
                self.type == 'recurrent' and self.amendment_state != 'next' and
                self.recurrent_sequence_type == 'recurring'):
            vals.update(self.get_amendment_vals(
                self.partner_bank_id,
                self.env['res.partner.bank'].browse(vals['partner_bank_id'])))
        return super(AccountBankingMandate, self).write(vals)
