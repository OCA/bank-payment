# -*- encoding: utf-8 -*-
##############################################################################
#
#    SEPA Direct Debit module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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

    type = fields.Selection([('recurrent', 'Recurrent'),
                             ('oneoff', 'One-Off')],
                            string='Type of Mandate', required=True,
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
                              string='Scheme', required=True, default="CORE")
    unique_mandate_reference = fields.Char(size=35)  # cf ISO 20022

    @api.one
    @api.constrains('type', 'recurrent_sequence_type')
    def _check_recurring_type(self):
        if (self.type == 'recurrent' and
                not self.recurrent_sequence_type):
            raise exceptions.Warning(
                _("The recurrent mandate '%s' must have a sequence type.")
                % self.unique_mandate_reference)

    @api.one
    @api.constrains('type', 'recurrent_sequence_type', 'sepa_migrated')
    def _check_migrated_to_sepa(self):
        if (self.type == 'recurrent' and not self.sepa_migrated and
                self.recurrent_sequence_type != 'first'):
            raise exceptions.Warning(
                _("The recurrent mandate '%s' which is not marked as "
                  "'Migrated to SEPA' must have its recurrent sequence type "
                  "set to 'First'.") % self.unique_mandate_reference)

    @api.one
    @api.constrains('type', 'original_mandate_identification', 'sepa_migrated')
    def _check_original_mandate_identification(self):
        if (self.type == 'recurrent' and not self.sepa_migrated and
                not self.original_mandate_identification):
            raise exceptions.Warning(
                _("You must set the 'Original Mandate Identification' on the "
                  "recurrent mandate '%s' which is not marked as 'Migrated to "
                  "SEPA'.") % self.unique_mandate_reference)

    @api.one
    @api.onchange('partner_bank_id')
    def mandate_partner_bank_change(self):
        super(AccountBankingMandate, self).mandate_partner_bank_change()
        res = {}
        if (self.state == 'valid' and
                self.partner_bank_id and
                self.type == 'recurrent' and
                self.recurrent_sequence_type != 'first'):
            self.recurrent_sequence_type = 'first'
            res['warning'] = {
                'title': _('Mandate update'),
                'message': _("As you changed the bank account attached to "
                             "this mandate, the 'Sequence Type' has been set "
                             "back to 'First'."),
            }
        return res

    @api.multi
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
