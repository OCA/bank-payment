# -*- coding: utf-8 -*-
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class mandate(orm.Model):
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
            'account_banking_mandate.mandate_valid':
            lambda self, cr, uid, obj, ctx=None:
            obj['state'] == 'valid',
            'account_banking_mandate.mandate_expired':
            lambda self, cr, uid, obj, ctx=None:
            obj['state'] == 'expired',
            'account_banking_mandate.mandate_cancel':
            lambda self, cr, uid, obj, ctx=None:
            obj['state'] == 'cancel',
        },
    }

    def _get_states(self, cr, uid, context=None):
        return [
            ('draft', _('Draft')),
            ('valid', _('Valid')),
            ('expired', _('Expired')),
            ('cancel', _('Cancelled')),
        ]

    _columns = {
        'partner_bank_id': fields.many2one(
            'res.partner.bank', 'Bank Account', track_visibility='onchange'),
        'partner_id': fields.related(
            'partner_bank_id', 'partner_id', type='many2one',
            relation='res.partner', string='Partner', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'unique_mandate_reference': fields.char(
            'Unique Mandate Reference', size=35, readonly=True,
            track_visibility='always'),
        'signature_date': fields.date(
            'Date of Signature of the Mandate', track_visibility='onchange'),
        'scan': fields.binary('Scan of the Mandate'),
        'last_debit_date': fields.date(
            'Date of the Last Debit', readonly=True),
        'state': fields.selection(
            lambda self, *a, **kw: self._get_states(*a, **kw),
            string='Status',
            help="Only valid mandates can be used in a payment line. A "
            "cancelled mandate is a mandate that has been cancelled by "
            "the customer."),
        'payment_line_ids': fields.one2many(
            'payment.line', 'mandate_id', "Related Payment Lines",
            readonly=True),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, context:
        self.pool['res.company']._company_default_get(
            cr, uid, 'account.banking.mandate', context=context),
        'unique_mandate_reference': '/',
        'state': 'draft',
    }

    _sql_constraints = [(
        'mandate_ref_company_uniq',
        'unique(unique_mandate_reference, company_id)',
        'A Mandate with the same reference already exists for this company !'
    )]

    def create(self, cr, uid, vals, context=None):
        if vals.get('unique_mandate_reference', '/') == '/':
            vals['unique_mandate_reference'] = \
                self.pool['ir.sequence'].next_by_code(
                    cr, uid, 'account.banking.mandate', context=context)
        return super(mandate, self).create(cr, uid, vals, context=context)

    def _check_dates(self, cr, uid, ids):
        for mandate in self.browse(cr, uid, ids):
            if (mandate.signature_date and
                    mandate.signature_date >
                    fields.date.context_today(self, cr, uid)):
                raise orm.except_orm(
                    _('Error:'),
                    _("The date of signature of mandate '%s' is in the "
                        "future !")
                    % mandate.unique_mandate_reference)

            if (mandate.signature_date and mandate.last_debit_date and
                    mandate.signature_date > mandate.last_debit_date):
                raise orm.except_orm(
                    _('Error:'),
                    _("The mandate '%s' can't have a date of last debit "
                        "before the date of signature.")
                    % mandate.unique_mandate_reference)
        return True

    def _check_valid_state(self, cr, uid, ids):
        for mandate in self.browse(cr, uid, ids):
            if mandate.state == 'valid' and not mandate.signature_date:
                raise orm.except_orm(
                    _('Error:'),
                    _("Cannot validate the mandate '%s' without a date of "
                        "signature.")
                    % mandate.unique_mandate_reference)
            if mandate.state == 'valid' and not mandate.partner_bank_id:
                raise orm.except_orm(
                    _('Error:'),
                    _("Cannot validate the mandate '%s' because it is not "
                        "attached to a bank account.")
                    % mandate.unique_mandate_reference)
        return True

    _constraints = [
        (_check_dates, "Error msg in raise",
            ['signature_date', 'last_debit_date']),
        (_check_valid_state, "Error msg in raise",
            ['state', 'partner_bank_id']),
    ]

    def mandate_partner_bank_change(
            self, cr, uid, ids, partner_bank_id, last_debit_date, state):
        res = {'value': {}}
        if partner_bank_id:
            partner_bank_read = self.pool['res.partner.bank'].read(
                cr, uid, partner_bank_id, ['partner_id'])['partner_id']
            res['value']['partner_id'] = partner_bank_read[0]
        return res

    def validate(self, cr, uid, ids, context=None):
        to_validate_ids = []
        for mandate in self.browse(cr, uid, ids, context=context):
            if mandate.state != 'draft':
                raise orm.except_orm(
                    _('StateError'),
                    _('Mandate should be in draft state')
                )
            to_validate_ids.append(mandate.id)
        self.write(
            cr, uid, to_validate_ids, {'state': 'valid'}, context=context)
        return True

    def cancel(self, cr, uid, ids, context=None):
        to_cancel_ids = []
        for mandate in self.browse(cr, uid, ids, context=context):
            if mandate.state not in ('draft', 'valid'):
                raise orm.except_orm(
                    _('StateError'),
                    _('Mandate should be in draft or valid state')
                )
            to_cancel_ids.append(mandate.id)
        self.write(
            cr, uid, to_cancel_ids, {'state': 'cancel'}, context=context)
        return True

    def back2draft(self, cr, uid, ids, context=None):
        ''' Allows to set the mandate back to the draft state.
        This is for mandates cancelled by mistake
        '''
        to_draft_ids = []
        for mandate in self.browse(cr, uid, ids, context=context):
            if mandate.state != 'cancel':
                raise orm.except_orm(
                    _('StateError'),
                    _('Mandate should be in cancel state')
                )
            to_draft_ids.append(mandate.id)
        self.write(
            cr, uid, to_draft_ids, {'state': 'draft'}, context=context)
        return True
