# -*- coding: utf-8 -*-
##############################################################################
#
#    French Letter of Change module for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import netsvc
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import base64

try:
    from unidecode import unidecode
except ImportError:
    unidecode = None

LCR_DATE_FORMAT = '%d%m%y'


class banking_export_lcr_wizard(orm.TransientModel):
    _name = 'banking.export.lcr.wizard'
    _description = 'Export French LCR File'

    _columns = {
        'state': fields.selection(
            [
                ('create', 'Create'),
                ('finish', 'Finish'),
            ],
            'State', readonly=True),
        'nb_transactions': fields.related(
            'file_id', 'nb_transactions', type='integer',
            string='Number of Transactions', readonly=True),
        'total_amount': fields.related(
            'file_id', 'total_amount', type='float', string='Total Amount',
            readonly=True),
        'file_id': fields.many2one(
            'banking.export.lcr', 'LCR CFONB File', readonly=True),
        'file': fields.related(
            'file_id', 'file', string="File", type='binary', readonly=True),
        'filename': fields.related(
            'file_id', 'filename', string="Filename", type='char', size=256,
            readonly=True),
        'payment_order_ids': fields.many2many(
            'payment.order', 'wiz_lcr_payorders_rel', 'wizard_id',
            'payment_order_id', 'Payment Orders', readonly=True),
    }

    _defaults = {
        'state': 'create',
    }

    def create(self, cr, uid, vals, context=None):
        payment_order_ids = context.get('active_ids', [])
        vals.update({
            'payment_order_ids': [[6, 0, payment_order_ids]],
        })
        return super(banking_export_lcr_wizard, self).create(
            cr, uid, vals, context=context)

    def _prepare_export_lcr(
            self, cr, uid, lcr_export, total_amount, transactions_count,
            cfonb_string, context=None):
        return {
            'total_amount': total_amount,
            'nb_transactions': transactions_count,
            'file': base64.encodestring(cfonb_string),
            'payment_order_ids': [(
                6, 0, [x.id for x in lcr_export.payment_order_ids]
            )],
        }

    def _prepare_field(
            self, cr, uid, field_name, field_value, size, context=None):
        '''This function is designed to be inherited.'''
        if not field_value:
            raise orm.except_orm(
                _('Error:'),
                _("The field '%s' is empty or 0. It should have a non-null "
                    "value.")
                % field_name)
        try:
            value = unidecode(field_value)
            unallowed_ascii_chars = [
                '"', '#', '$', '%', '&', ';', '<', '>', '=', '@',
                '[', ']', '^', '_', '`', '{', '}', '|', '~', '\\', '!',
            ]
            for unallowed_ascii_char in unallowed_ascii_chars:
                value = value.replace(unallowed_ascii_char, '-')
        except:
            raise orm.except_orm(
                _('Error:'),
                _("Cannot convert the field '%s' to ASCII")
                % field_name)
        value = value.upper()
        # Cut if too long
        value = value[0:size]
        # enlarge if too small
        if len(value) < size:
            value = value.ljust(size, ' ')
        assert len(value) == size, 'The length of the field is wrong'
        return value

    def _get_rib_from_iban(self, cr, uid, partner_bank, context=None):
        # I do NOT want to add a dependancy on l10n_fr_rib, because
        # we plan to remove the module in the near future
        # So I consider that IBAN MUST be given in the res.partner.bank
        # of type 'rib'
        if partner_bank.state == 'rib' and not partner_bank.acc_number:
            raise orm.except_orm(
                _('Error:'),
                _("For the bank account '%s' of partner '%s', the bank "
                    "account type is 'RIB and optional IBAN' and the IBAN "
                    "field is empty, but, starting from 2014, we consider "
                    "that the IBAN is required. Please write the IBAN on "
                    "this bank account.")
                % (self.pool['res.partner.bank'].name_get(
                    cr, uid, [partner_bank.id], context=context)[0][1],
                    partner_bank.partner_id.name))
        elif partner_bank.state != 'iban':
            raise orm.except_orm(
                _('Error:'),
                _("For the bank account '%s' of partner '%s', the Bank "
                    "Account Type should be 'IBAN'.")
                % (self.pool['res.partner.bank'].name_get(
                    cr, uid, [partner_bank.id], context=context)[0][1],
                    partner_bank.partner_id.name))
        iban = partner_bank.acc_number.replace(' ', '')
        if iban[0:2] != 'FR':
            raise orm.except_orm(
                _('Error:'),
                _("LCR are only for French bank accounts. The IBAN '%s' "
                    "of partner '%s' is not a French IBAN.")
                % (partner_bank.acc_number, partner_bank.partner_id.name))
        assert len(iban) == 27, 'French IBANs must have 27 caracters'
        return {
            'code_banque': iban[4:9],
            'code_guichet': iban[9:14],
            'numero_compte': iban[14:25],
            'cle_rib': iban[25:27],
        }

    def _prepare_first_cfonb_line(
            self, cr, uid, lcr_export, context=None):
        '''Generate the header line of the CFONB file'''
        code_enregistrement = '03'
        code_operation = '60'
        numero_enregistrement = '00000001'
        numero_emetteur = '000000'  # It is not needed for LCR
        # this number is only required for old national direct debits
        today_str = fields.date.context_today(self, cr, uid, context=context)
        today_dt = datetime.strptime(today_str, DEFAULT_SERVER_DATE_FORMAT)
        date_remise = today_dt.strftime(LCR_DATE_FORMAT)
        raison_sociale_cedant = self._prepare_field(
            cr, uid, u'Raison sociale du cédant',
            lcr_export.payment_order_ids[0].company_id.name, 24,
            context=context)
        domiciliation_bancaire_cedant = self._prepare_field(
            cr, uid, u'Domiciliation bancaire du cédant',
            lcr_export.payment_order_ids[0].mode.bank_id.bank.name, 24,
            context=context)
        code_entree = '3'
        code_dailly = ' '
        code_monnaie = 'E'
        rib = self._get_rib_from_iban(
            cr, uid, lcr_export.payment_order_ids[0].mode.bank_id,
            context=context)
        ref_remise = self._prepare_field(
            cr, uid, u'Référence de la remise',
            lcr_export.payment_order_ids[0].reference, 11, context=context)
        cfonb_line = ''.join([
            code_enregistrement,
            code_operation,
            numero_enregistrement,
            numero_emetteur,
            ' ' * 6,
            date_remise,
            raison_sociale_cedant,
            domiciliation_bancaire_cedant,
            code_entree,
            code_dailly,
            code_monnaie,
            rib['code_banque'],
            rib['code_guichet'],
            rib['numero_compte'],
            ' ' * (16 + 6 + 10 + 15),
            # Date de valeur is left empty because it is only for
            # "remise à l'escompte" and we do
            # "Encaissement, crédit forfaitaire après l’échéance"
            ref_remise,
        ])
        assert len(cfonb_line) == 160, 'LCR CFONB line must have 160 chars'
        cfonb_line += '\r\n'
        return cfonb_line

    def _prepare_cfonb_line(
            self, cr, uid, line, requested_date, transactions_count,
            context=None):
        '''Generate each debit line of the CFONB file'''
        # I use French variable names because the specs are in French
        code_enregistrement = '06'
        code_operation = '60'
        numero_enregistrement = '%08d' % (transactions_count + 1)
        reference_tire = self._prepare_field(
            cr, uid, u'Référence tiré', line.communication, 10,
            context=context)
        rib = self._get_rib_from_iban(cr, uid, line.bank_id, context=context)

        nom_tire = self._prepare_field(
            cr, uid, u'Nom tiré', line.partner_id.name, 24, context=context)
        nom_banque = self._prepare_field(
            cr, uid, u'Nom banque', line.bank_id.bank.name, 24,
            context=context)
        code_acceptation = '0'
        montant_centimes = int(line.amount_currency * 100)
        zero_montant_centimes = ('%012d' % montant_centimes)
        today_str = fields.date.context_today(self, cr, uid, context=context)
        today_dt = datetime.strptime(today_str, DEFAULT_SERVER_DATE_FORMAT)
        date_creation = today_dt.strftime(LCR_DATE_FORMAT)
        requested_date_dt = datetime.strptime(
            requested_date, DEFAULT_SERVER_DATE_FORMAT)
        date_echeance = requested_date_dt.strftime(LCR_DATE_FORMAT)
        reference_tireur = reference_tire

        cfonb_line = ''.join([
            code_enregistrement,
            code_operation,
            numero_enregistrement,
            ' ' * (6 + 2),
            reference_tire,
            nom_tire,
            nom_banque,
            code_acceptation,
            ' ' * 2,
            rib['code_banque'],
            rib['code_guichet'],
            rib['numero_compte'],
            zero_montant_centimes,
            ' ' * 4,
            date_echeance,
            date_creation,
            ' ' * (4 + 1 + 3 + 3 + 9),
            reference_tireur,
        ])
        assert len(cfonb_line) == 160, 'LCR CFONB line must have 160 chars'
        cfonb_line += '\r\n'
        return cfonb_line

    def _prepare_final_cfonb_line(
            self, cr, uid, total_amount, transactions_count, context=None):
        '''Generate the last line of the CFONB file'''
        code_enregistrement = '08'
        code_operation = '60'
        numero_enregistrement = '%08d' % (transactions_count + 2)
        montant_total_centimes = int(total_amount * 100)
        zero_montant_total_centimes = ('%012d' % montant_total_centimes)
        cfonb_line = ''.join([
            code_enregistrement,
            code_operation,
            numero_enregistrement,
            ' ' * (6 + 12 + 24 + 24 + 1 + 2 + 5 + 5 + 11),
            zero_montant_total_centimes,
            ' ' * (4 + 6 + 10 + 15 + 5 + 6),
        ])
        assert len(cfonb_line) == 160, 'LCR CFONB line must have 160 chars'
        return cfonb_line

    def create_lcr(self, cr, uid, ids, context=None):
        '''Creates the LCR CFONB file.'''
        lcr_export = self.browse(cr, uid, ids[0], context=context)
        today = fields.date.context_today(self, cr, uid, context=context)

        cfonb_string = self._prepare_first_cfonb_line(
            cr, uid, lcr_export, context=context)
        transactions_count = 0
        total_amount = 0.0
        for payment_order in lcr_export.payment_order_ids:
            total_amount = total_amount + payment_order.total
            # Iterate each payment lines
            for line in payment_order.line_ids:
                if line.currency.name != 'EUR':
                    raise orm.except_orm(
                        _('Error:'),
                        _("The currency of payment line '%s' is '%s'. "
                            "To be included in a French LCR, the currency "
                            "must be EUR.")
                        % (line.name, line.currency.name))
                transactions_count += 1
                if payment_order.date_prefered == 'due':
                    requested_date = line.ml_maturity_date or today
                elif payment_order.date_prefered == 'fixed':
                    requested_date = payment_order.date_scheduled or today
                else:
                    requested_date = today
                cfonb_string += self._prepare_cfonb_line(
                    cr, uid, line, requested_date, transactions_count,
                    context=context)

        cfonb_string += self._prepare_final_cfonb_line(
            cr, uid, total_amount, transactions_count,
            context=context)

        file_id = self.pool['banking.export.lcr'].create(
            cr, uid, self._prepare_export_lcr(
                cr, uid, lcr_export, total_amount, transactions_count,
                cfonb_string, context=context),
            context=context)

        self.write(
            cr, uid, ids, {
                'file_id': file_id,
                'state': 'finish',
            }, context=context)

        action = {
            'name': 'LCR File',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': self._name,
            'res_id': ids[0],
            'target': 'new',
        }

        return action

    def cancel_lcr(self, cr, uid, ids, context=None):
        '''Cancel the CFONB file: just drop the file'''
        lcr_export = self.browse(cr, uid, ids[0], context=context)
        self.pool['banking.export.lcr'].unlink(
            cr, uid, lcr_export.file_id.id, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def save_lcr(self, cr, uid, ids, context=None):
        '''Mark the LCR file as 'sent' and the payment order as 'done'.'''
        lcr_export = self.browse(cr, uid, ids[0], context=context)
        self.pool['banking.export.lcr'].write(
            cr, uid, lcr_export.file_id.id, {'state': 'sent'},
            context=context)
        wf_service = netsvc.LocalService('workflow')
        for order in lcr_export.payment_order_ids:
            wf_service.trg_validate(uid, 'payment.order', order.id, 'done', cr)
        return {'type': 'ir.actions.act_window_close'}
