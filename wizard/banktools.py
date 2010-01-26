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

from tools.translate import _

__all__ = [
    'get_period', 
    'get_bank_account',
    'get_or_create_partner',
    'get_company_bank_account',
    'create_bank_account',
    'struct',
]

class struct(dict):
    '''
    Ease working with dicts. Allow dict.key alongside dict['key']
    '''
    def __setattr__(self, item, value):
        self.__setitem__(item, value)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def show(self, indent=0, align=False, ralign=False):
        '''
        PrettyPrint method. Aligns keys right (ralign) or left (align).
        '''
        if align or ralign:
            width = 0
            for key in self.iterkeys():
                width = max(width, len(key))
            alignment = ''
            if not ralign:
                alignment = '-'
            fmt = '%*.*s%%%s%d.%ds: %%s' % (
                indent, indent, '', alignment, width, width
            )
        else:
            fmt = '%*.*s%%s: %%s' % (indent, indent, '')
        for item in self.iteritems():
            print fmt % item

import datetime
from account_banking import sepa
from account_banking.parsers.convert import *

def get_period(pool, cursor, uid, date, company, log):
    '''
    Get a suitable period for the given date range and the given company.
    '''
    fiscalyear_obj = pool.get('account.fiscalyear')
    period_obj = pool.get('account.period')
    if not date:
        date = date2str(datetime.datetime.today())

    search_date = date2str(date)
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
            _('No suitable fiscal year found for company %(company_name)s')
            % dict(company_name=company.name)
        )
        return False
    elif len(fiscalyear_ids) > 1:
        log.append(
            _('Multiple overlapping fiscal years found for date %(date)s')
            % dict(date=date)
        )
        return False

    fiscalyear_id = fiscalyear_ids[0]
    period_ids = period_obj.search(cursor, uid, [
        ('date_start','<=',search_date), ('date_stop','>=',search_date),
        ('fiscalyear_id','=',fiscalyear_id), ('state','=','draft')
    ])
    if not period_ids:
        log.append(_('No suitable period found for date %(date)s')
                   % dict(date=date)
        )
        return False
    if len(period_ids) != 1:
        log.append(_('Multiple overlapping periods for date %(date)s')
                   % dict(date=date)
        )
        return False
    return period_ids[0]

def get_bank_account(pool, cursor, uid, account_number, log, fail=False):
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
    elif len(bank_account_ids) != 1:
        log.append(
            _('More than one bank account was found with the same number %(account_no)s')
            % dict(account_no=account_number)
        )
        return False
    return partner_bank_obj.browse(cursor, uid, bank_account_ids)[0]

def get_or_create_partner(pool, cursor, uid, name, log):
    '''
    Get or create the partner belonging to the account holders name <name>
    '''
    partner_obj = pool.get('res.partner')
    partner_ids = partner_obj.search(cursor, uid, [('name', 'ilike', name)])
    if not partner_ids:
        partner_id = partner_obj.create(cursor, uid, dict(
            name=name, active=True, comment='Generated by Import Bank Statements File',
        ))
    elif len(partner_ids) > 1:
        log.append(
            _('More then one possible match found for partner with name %(name)s')
            % {'name': name}
        )
        return False
    else:
        partner_id = partner_ids[0]
    return partner_obj.browse(cursor, uid, partner_id)[0]

def get_company_bank_account(pool, cursor, uid, account_number,
                             company, log):
    '''
    Get the matching bank account for this company.
    '''
    results = struct()
    bank_account = get_bank_account(pool, cursor, uid, account_number, log,
                                    fail=True)
    if not bank_account:
        return False
    if bank_account.partner_id.id != company.partner_id.id:
        log.append(
            _('Account %(account_no)s is not owned by %(partner)s')
            % dict(account_no = account_number,
                   partner = company.partner_id.name,
        ))
        return False
    results.account = bank_account
    bank_settings_obj = pool.get('account.banking.account.settings')
    bank_settings_ids = bank_settings_obj.search(cursor, uid, [
        ('partner_bank_id', '=', bank_account.id)
    ])
    if bank_settings_ids:
        settings = bank_settings_obj.browse(cursor, uid, bank_settings_ids)[0]
        results.journal_id = settings.journal_id
        results.default_debit_account_id = settings.default_debit_account_id
        results.default_credit_account_id = settings.default_credit_account_id
    return results

def get_iban_bic_NL(bank_acc):
    '''
    Consult the Dutch online banking database to check both the account number
    and the bank to which it belongs. Will not work offline, is limited to
    banks operating in the Netherlands and will only convert Dutch local
    account numbers.
    '''
    import urllib, urllib2
    from BeautifulSoup import BeautifulSoup

    IBANlink = 'http://www.ibannl.org/iban_check.php'
    data = urllib.urlencode(dict(number=bank_acc, method='POST'))
    request = urllib2.Request(IBANlink, data)
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response)
    result = struct()
    for _pass, td in enumerate(soup.findAll('td')):
        if _pass % 2 == 1:
            result[attr] = td.find('font').contents[0]
        else:
            attr = td.find('strong').contents[0][:4].strip().lower()
    if result:
        result.account = bank_acc
        result.country_id = result.bic[4:6]
        # Nationalized bank code
        result.code = result.bic[:6]
        # All Dutch banks use generic channels
        result.bic += 'XXX'
        return result
    return None

online_account_info = {
    # TODO: Add more online data banks
    'NL': get_iban_bic_NL,
}

def create_bank_account(pool, cursor, uid, partner_id,
                        account_number, holder_name, log
                        ):
    '''
    Create a matching bank account with this holder for this partner.
    '''
    values = struct(
        partner_id = partner_id,
        owner_name = holder_name,
    )
    # Are we dealing with IBAN?
    iban = sepa.IBAN(account_number)
    if iban.valid:
        values.state = 'iban'
        values.acc_number = iban.BBAN
        bankcode = iban.bankcode + iban.countrycode
    else:
        # No, try to convert to IBAN
        country = pool.get('res.partner').browse(
            cursor, uid, partner_id).country_id
        values.state = 'bank'
        values.acc_number = account_number
        if country.code in sepa.IBAN.countries \
           and country.code in online_account_info \
           :
            account_info = online_account_info[country.code](values.acc_number)
            if account_info and iban in account_info:
                values.iban = iban = account_info.iban
                values.state = 'iban'
                bankcode = account_info.code
                bic = account_info.bic
            else:
                bankcode = None
                bic = None

    if bankcode:
        # Try to link bank
        bank_obj = pool.get('res.bank')
        bank_ids = bank_obj.search(cursor, uid, [
            ('code', 'ilike', bankcode)
        ])
        if not bank_ids and bic:
            bank_ids = bank_obj.search(cursor, uid, [
                ('bic', 'ilike', bic)
            ])
        if bank_ids:
            # Check BIC on existing banks
            values.bank_id = bank_ids[0]
            bank = bank_obj.browse(cursor, uid, values.bank_id)
            if not bank.bic:
                bank_obj.write(cursor, uid, values.bank_id, dict(bic=bic))
        else:
            # New bank - create
            values.bank_id = bank_obj.create(cursor, uid, dict(
                code = account_info.code,
                bic = account_info.bic,
                name = account_info.bank,
                country_id = country.id,
            ))

    # Create bank account and return
    return pool.get('res.partner.bank').create(cursor, uid, values)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
