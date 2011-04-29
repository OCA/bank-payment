# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import sys
import datetime
import re
from tools.translate import _
from account_banking.parsers import convert
from account_banking import sepa
from account_banking.struct import struct
import unicodedata

__all__ = [
    'get_period', 
    'get_bank_accounts',
    'get_or_create_partner',
    'get_company_bank_account',
    'create_bank_account',
]

def get_period(pool, cursor, uid, date, company, log):
    '''
    Get a suitable period for the given date range and the given company.
    '''
    fiscalyear_obj = pool.get('account.fiscalyear')
    period_obj = pool.get('account.period')
    if not date:
        date = convert.date2str(datetime.datetime.today())

    search_date = convert.date2str(date)
    fiscalyear_ids = fiscalyear_obj.search(cursor, uid, [
        ('date_start','<=', search_date), ('date_stop','>=', search_date),
        ('state','=','draft'), ('company_id','=',company.id)
    ])
    if not fiscalyear_ids:
        fiscalyear_ids = fiscalyear_obj.search(cursor, uid, [
            ('date_start','<=',search_date), ('date_stop','>=',search_date),
            ('state','=','draft'), ('company_id','=',None)
        ])
    if not fiscalyear_ids:
        log.append(
            _('No suitable fiscal year found for date %(date)s and company %(company_name)s')
            % dict(company_name=company.name, date=date)
        )
        return False
    elif len(fiscalyear_ids) > 1:
        log.append(
            _('Multiple overlapping fiscal years found for date %(date)s and company %(company_name)s')
            % dict(company_name=company.name, date=date)
        )
        return False

    fiscalyear_id = fiscalyear_ids[0]
    period_ids = period_obj.search(cursor, uid, [
        ('date_start','<=',search_date), ('date_stop','>=',search_date),
        ('fiscalyear_id','=',fiscalyear_id), ('state','=','draft')
    ])
    if not period_ids:
        log.append(_('No suitable period found for date %(date)s and company %(company_name)s')
                   % dict(company_name=company.name, date=date)
        )
        return False
    if len(period_ids) != 1:
        log.append(_('Multiple overlapping periods for date %(date)s and company %(company_name)s')
                   % dict(company_name=company.name, date=date)
        )
        return False
    return period_ids[0]

def get_bank_accounts(pool, cursor, uid, account_number, log, fail=False):
    '''
    Get the bank account with account number account_number
    '''
    # No need to search for nothing
    if not account_number:
        return False

    partner_bank_obj = pool.get('res.partner.bank')
    bank_account_ids = partner_bank_obj.search(cursor, uid, [
        ('acc_number', '=', account_number)
    ])
    if not bank_account_ids:
        bank_account_ids = partner_bank_obj.search(cursor, uid, [
            ('iban', '=', account_number)
        ])
    if not bank_account_ids:
        if not fail:
            log.append(
                _('Bank account %(account_no)s was not found in the database')
                % dict(account_no=account_number)
            )
        return False
    return partner_bank_obj.browse(cursor, uid, bank_account_ids)

def _has_attr(obj, attr):
    # Needed for dangling addresses and a weird exception scheme in
    # OpenERP's orm.
    try:
        return bool(getattr(obj, attr))
    except KeyError:
        return False

def get_or_create_partner(pool, cursor, uid, name, address, postal_code, city,
                          country_code, log):
    '''
    Get or create the partner belonging to the account holders name <name>
    '''
    partner_obj = pool.get('res.partner')
    partner_ids = partner_obj.search(cursor, uid, [('name', 'ilike', name)])
    if not partner_ids:
        # Try brute search on address and then match reverse
        address_obj = pool.get('res.partner.address')
        filter = [('partner_id', '<>', None)]
        if country_code:
            country_obj = pool.get('res.country')
            country_ids = country_obj.search(
                cursor, uid, [('code','=',country_code.upper())]
            )
            country_id = country_ids and country_ids[0] or False
            filter.append(('country_id', '=', country_id))
        if address:
            if len(address) >= 1:
                filter.append(('street', 'ilike', addres[0]))
            if len(address) > 1:
                filter.append(('street2', 'ilike', addres[1]))
        if city:
            filter.append(('city', 'ilike', city))
        if postal_code:
            filter.append(('zip', 'ilike', postal_code))
        address_ids = address_obj.search(cursor, uid, filter)
        key = name.lower()

        # Make sure to get a unique list
        partner_ids = list(set([x.partner_id.id
                       for x in address_obj.browse(cursor, uid, address_ids)
                       # Beware for dangling addresses
                       if _has_attr(x.partner_id, 'name') and
                          x.partner_id.name.lower() in key
                      ]))
    if not partner_ids:
        if (not country_code) or not country_id:
            user = pool.get('res.user').browse(cursor, uid, uid)
            country_id = (
                user.company_id and
                user.company_id.partner_id and
                user.company_id.partner_id.country and 
                user.company_id.partner_id.country.id or
                False
            )
        partner_id = partner_obj.create(cursor, uid, dict(
            name=name, active=True, comment='Generated from Bank Statements Import',
            address=[(0,0,{
                'street': address and address[0] or '',
                'street2': len(address) > 1 and address[1] or '',
                'city': city,
                'zip': postal_code or '',
                'country_id': country_id,
            })],
        ))
    elif len(partner_ids) > 1:
        log.append(
            _('More then one possible match found for partner with name %(name)s')
            % {'name': name}
        )
        return False
    else:
        partner_id = partner_ids[0]
    return partner_id

def get_company_bank_account(pool, cursor, uid, account_number, currency,
                             company, log):
    '''
    Get the matching bank account for this company. Currency is the ISO code
    for the requested currency.
    '''
    results = struct()
    bank_accounts = get_bank_accounts(pool, cursor, uid, account_number, log,
                                      fail=True)
    if not bank_accounts:
        return False
    elif len(bank_accounts) != 1:
        log.append(
            _('More than one bank account was found with the same number %(account_no)s')
            % dict(account_no = account_number)
        )
        return False
    if bank_accounts[0].partner_id.id != company.partner_id.id:
        log.append(
            _('Account %(account_no)s is not owned by %(partner)s')
            % dict(account_no = account_number,
                   partner = company.partner_id.name,
        ))
        return False
    results.account = bank_accounts[0]
    bank_settings_obj = pool.get('account.banking.account.settings')
    criteria = [('partner_bank_id', '=', bank_accounts[0].id)]

    # Find matching journal for currency
    journal_obj = pool.get('account.journal')
    journal_ids = journal_obj.search(cursor, uid, [
        ('type', '=', 'bank'),
        ('currency', '=', currency or company.currency_id.name)
    ])
    if not journal_ids and currency == company.currency_id.name:
        journal_ids = journal_obj.search(cursor, uid, [
            ('type', '=', 'bank'), ('currency', '=', False)
        ])
    if journal_ids:
        criteria.append(('journal_id', 'in', journal_ids))

    # Find bank account settings
    bank_settings_ids = bank_settings_obj.search(cursor, uid, criteria)
    if bank_settings_ids:
        settings = bank_settings_obj.browse(cursor, uid, bank_settings_ids)[0]
        results.company_id = company
        results.journal_id = settings.journal_id
        # Take currency from settings or from company
        if settings.journal_id.currency.id:
            results.currency_id = settings.journal_id.currency
        else:
            results.currency_id = company.currency_id
        # Rest just copy/paste from settings. Why am I doing this?
        results.default_debit_account_id = settings.default_debit_account_id
        results.default_credit_account_id = settings.default_credit_account_id
        results.costs_account_id = settings.costs_account_id
        results.invoice_journal_id = settings.invoice_journal_id
        results.bank_partner_id = settings.bank_partner_id
    return results

def get_or_create_bank(pool, cursor, uid, bic, online=False, code=None,
                       name=None):
    '''
    Find or create the bank with the provided BIC code.
    When online, the SWIFT database will be consulted in order to
    provide for missing information.
    '''
    # UPDATE: Free SWIFT databases are since 2/22/2010 hidden behind an
    #         image challenge/response interface.

    bank_obj = pool.get('res.bank')

    # Self generated key?
    if len(bic) < 8:
        # search key
        bank_ids = bank_obj.search(
            cursor, uid, [
                ('code', '=', bic[:6])
            ])
        if not bank_ids:
            bank_ids = bank_obj.search(
                cursor, uid, [
                    ('bic', 'ilike', bic + '%')
                ])
    else:
        bank_ids = bank_obj.search(
            cursor, uid, [
                ('bic', '=', bic)
            ])

    if bank_ids and len(bank_ids) == 1:
        banks = bank_obj.browse(cursor, uid, bank_ids)
        return banks[0].id, banks[0].country.id

    country_obj = pool.get('res.country')
    country_ids = country_obj.search(
        cursor, uid, [('code', '=', bic[4:6])]
    )
    country_id = country_ids and country_ids[0] or False
    bank_id = False

    if online:
        info, address = sepa.online.bank_info(bic)
        if info:
            bank_id = bank_obj.create(cursor, uid, dict(
                code = info.code,
                name = info.name,
                street = address.street,
                street2 = address.street2,
                zip = address.zip,
                city = address.city,
                country = country_id,
                bic = info.bic[:8],
            ))
    else:
        info = struct(name=name, code=code)

    if not online or not bank_id:
        bank_id = bank_obj.create(cursor, uid, dict(
            code = info.code or 'UNKNOW',
            name = info.name or _('Unknown Bank'),
            country = country_id,
            bic = bic,
        ))
    return bank_id, country_id

def create_bank_account(pool, cursor, uid, partner_id,
                        account_number, holder_name, address, city,
                        country_code, log
                        ):
    '''
    Create a matching bank account with this holder for this partner.
    '''
    values = struct(
        partner_id = partner_id,
        owner_name = holder_name,
    )
    bankcode = None
    bic = None
    country_obj = pool.get('res.country')

    # Are we dealing with IBAN?
    iban = sepa.IBAN(account_number)
    if iban.valid:
        # Take as much info as possible from IBAN
        values.state = 'iban'
        values.iban = str(iban)
        values.acc_number = iban.BBAN
        bankcode = iban.bankcode + iban.countrycode
        country_code = iban.countrycode

    if not country_code:
        country = pool.get('res.partner').browse(
            cursor, uid, partner_id).country
        country_code = country.code
        country_id = country.id
    else:
        if iban.valid:
            country_ids = country_obj.search(cursor, uid,
                                             [('code', '=', iban.countrycode)]
                                             )
        else:
            country_ids = country_obj.search(cursor, uid,
                                             [('code', '=', country_code)]
                                             )
        country_id = country_ids[0]
    
    account_info = False
    if not iban.valid:
        # No, try to convert to IBAN
        values.state = 'bank'
        values.acc_number = account_number
        if country_code in sepa.IBAN.countries:
            account_info = sepa.online.account_info(country_code,
                                                    values.acc_number
                                                   )
            if account_info:
                values.iban = iban = account_info.iban
                values.state = 'iban'
                bankcode = account_info.code
                bic = account_info.bic

    if bic:
        values.bank = get_or_create_bank(pool, cursor, uid, bic)[0]

    else:
        if not bankcode:
            bankcode = "UNKNOW"
        # Try to link bank
        bank_obj = pool.get('res.bank')
        bank_ids = bank_obj.search(cursor, uid, [
            ('code', 'ilike', bankcode)
        ])
        if bank_ids:
            # Check BIC on existing banks
            values.bank = bank_ids[0]
            bank = bank_obj.browse(cursor, uid, values.bank)
            if not bank.bic:
                bank_obj.write(cursor, uid, values.bank, dict(bic=bic))
        else:
            # New bank - create
            res = struct(country_id=country_id)
            if account_info:
                res.code = account_info.code
                # Only the first eight positions of BIC are used for bank
                # transfers, so ditch the rest.
                res.bic = account_info.bic[:8]
                res.name = account_info.bank
            else:
                res.code = bankcode
                res.name = _('Unknown Bank')

            values.bank = bank_obj.create(cursor, uid, res)

    # Create bank account and return
    return pool.get('res.partner.bank').create(cursor, uid, values)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
