# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2014 Therp BV (<http://therp.nl>).
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
from openerp import SUPERUSER_ID
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.addons.account_banking_iban_lookup import online
from openerp.addons.account_banking import sepa
from openerp.addons.account_banking.wizard.banktools import get_or_create_bank


def warning(title, message):
    '''Convenience routine'''
    return {'warning': {'title': title, 'message': message}}


class res_partner_bank(orm.Model):
    '''
    Extended functionality:
        1. BBAN and IBAN are considered equal
        2. Online lookup when an API is available (providing NL in this module)
        3. Banks are created on the fly when using IBAN + online
        4. IBAN formatting
        5. BBAN's are generated from IBAN when possible
    '''
    _inherit = 'res.partner.bank'

    def init(self, cr):
        '''
        Update existing iban accounts to comply to new regime
        '''

        partner_bank_obj = self.pool.get('res.partner.bank')
        bank_ids = partner_bank_obj.search(
            cr, SUPERUSER_ID, [('state', '=', 'iban')], limit=0)
        for bank in partner_bank_obj.read(cr, SUPERUSER_ID, bank_ids):
            write_vals = {}
            if bank['state'] == 'iban':
                iban_acc = sepa.IBAN(bank['acc_number'])
                if iban_acc.valid:
                    write_vals['acc_number_domestic'] = iban_acc.localized_BBAN
                    write_vals['acc_number'] = str(iban_acc)
                elif bank['acc_number'] != bank['acc_number'].upper():
                    write_vals['acc_number'] = bank['acc_number'].upper()
                if write_vals:
                    partner_bank_obj.write(
                        cr, SUPERUSER_ID, bank['id'], write_vals)

    @staticmethod
    def _correct_IBAN(acc_number):
        '''
        Routine to correct IBAN values and deduce localized values when valid.
        Note: No check on validity IBAN/Country
        '''
        iban = sepa.IBAN(acc_number)
        return (str(iban), iban.localized_BBAN)

    def create(self, cr, uid, vals, context=None):
        '''
        Create dual function IBAN account for SEPA countries
        '''
        if vals.get('state') == 'iban':
            iban = (vals.get('acc_number') or
                    vals.get('acc_number_domestic', False))
            vals['acc_number'], vals['acc_number_domestic'] = (
                self._correct_IBAN(iban))
        return super(res_partner_bank, self).create(
            cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        '''
        Create dual function IBAN account for SEPA countries

        Update the domestic account number when the IBAN is
        written, or clear the domestic number on regular account numbers.
        '''
        if ids and isinstance(ids, (int, long)):
            ids = [ids]
        for account in self.read(
                cr, uid, ids, ['state', 'acc_number']):
            if 'state' in vals or 'acc_number' in vals:
                account.update(vals)
                if account['state'] == 'iban':
                    vals['acc_number'], vals['acc_number_domestic'] = (
                        self._correct_IBAN(account['acc_number']))
                else:
                    vals['acc_number_domestic'] = False
            super(res_partner_bank, self).write(
                cr, uid, account['id'], vals, context)
        return True

    def onchange_acc_number(
            self, cr, uid, ids, acc_number, acc_number_domestic,
            state, partner_id, country_id, context=None):
        if state == 'iban':
            return self.onchange_iban(
                cr, uid, ids, acc_number, acc_number_domestic,
                state, partner_id, country_id, context=None
            )
        else:
            return self.onchange_domestic(
                cr, uid, ids, acc_number,
                partner_id, country_id, context=None
            )

    def onchange_domestic(
            self, cr, uid, ids, acc_number,
            partner_id, country_id, context=None):
        '''
        Trigger to find IBAN. When found:
            1. Reformat BBAN
            2. Autocomplete bank

        TODO: prevent unnecessary assignment of country_ids and
        browsing of the country
        '''
        if not acc_number:
            return {}

        values = {}
        country_obj = self.pool.get('res.country')
        country_ids = []
        country = False

        # Pre fill country based on available data. This is just a default
        # which can be overridden by the user.
        # 1. Use provided country_id (manually filled)
        if country_id:
            country = country_obj.browse(cr, uid, country_id, context=context)
            country_ids = [country_id]
        # 2. Use country_id of found bank accounts
        # This can be usefull when there is no country set in the partners
        # addresses, but there was a country set in the address for the bank
        # account itself before this method was triggered.
        elif ids and len(ids) == 1:
            partner_bank_obj = self.pool.get('res.partner.bank')
            partner_bank_id = partner_bank_obj.browse(
                cr, uid, ids[0], context=context)
            if partner_bank_id.country_id:
                country = partner_bank_id.country_id
                country_ids = [country.id]
        # 3. Use country_id of default address of partner
        # The country_id of a bank account is a one time default on creation.
        # It originates in the same address we are about to check, but
        # modifications on that address afterwards are not transfered to the
        # bank account, hence the additional check.
        elif partner_id:
            partner_obj = self.pool.get('res.partner')
            country = partner_obj.browse(
                cr, uid, partner_id, context=context).country
            country_ids = country and [country.id] or []
        # 4. Without any of the above, take the country from the company of
        # the handling user
        if not country_ids:
            user = self.pool.get('res.users').browse(
                cr, uid, uid, context=context)
            # Try user companies partner (user no longer has address in 6.1)
            if (user.company_id and
                    user.company_id.partner_id and
                    user.company_id.partner_id.country):
                country_ids = [user.company_id.partner_id.country.id]
            else:
                if (user.company_id and user.company_id.partner_id and
                        user.company_id.partner_id.country):
                    country_ids = [user.company_id.partner_id.country.id]
                else:
                    # Ok, tried everything, give up and leave it to the user
                    return warning(_('Insufficient data'),
                                   _('Insufficient data to select online '
                                     'conversion database')
                                   )
        result = {'value': values}
        # Complete data with online database when available
        if country_ids:
            country = country_obj.browse(
                cr, uid, country_ids[0], context=context)
            values['country_id'] = country_ids[0]
        if country and country.code in sepa.IBAN.countries:
            info = online.account_info(country.code, acc_number)
            if info:
                iban_acc = sepa.IBAN(info.iban)
                if iban_acc.valid:
                    values['acc_number_domestic'] = iban_acc.localized_BBAN
                    values['acc_number'] = unicode(iban_acc)
                    values['state'] = 'iban'
                    bank_id, country_id = get_or_create_bank(
                        self.pool, cr, uid,
                        info.bic or iban_acc.BIC_searchkey,
                        name=info.bank)
                    if country_id:
                        values['country_id'] = country_id
                    values['bank'] = bank_id or False
                    if info.bic:
                        values['bank_bic'] = info.bic
                else:
                    info = None
            if info is None:
                result.update(warning(
                    _('Invalid data'),
                    _('The account number appears to be invalid for %s')
                    % country.name
                ))
            if info is False:
                if country.code in sepa.IBAN.countries:
                    acc_number_fmt = sepa.BBAN(acc_number, country.code)
                    if acc_number_fmt.valid:
                        values['acc_number_domestic'] = str(acc_number_fmt)
                    else:
                        result.update(warning(
                            _('Invalid format'),
                            _('The account number has the wrong format for %s')
                            % country.name
                        ))
        return result

    def onchange_iban(
            self, cr, uid, ids, acc_number, acc_number_domestic,
            state, partner_id, country_id, context=None):
        '''
        Trigger to verify IBAN. When valid:
            1. Extract BBAN as local account
            2. Auto complete bank
        '''
        if not acc_number:
            return {}

        iban_acc = sepa.IBAN(acc_number)
        if iban_acc.valid:
            bank_id, country_id = get_or_create_bank(
                self.pool, cr, uid, iban_acc.BIC_searchkey,
                code=iban_acc.BIC_searchkey
            )
            return {
                'value': dict(
                    acc_number_domestic=iban_acc.localized_BBAN,
                    acc_number=unicode(iban_acc),
                    country=country_id or False,
                    bank=bank_id or False,
                )
            }
        return warning(
            _('Invalid IBAN account number!'),
            _("The IBAN number doesn't seem to be correct"))

    def online_account_info(
            self, cr, uid, country_code, acc_number, context=None):
        """
        Overwrite API hook from account_banking
        """
        return online.account_info(country_code, acc_number)
