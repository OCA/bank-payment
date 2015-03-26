# -*- coding: utf-8 -*-
##############################################################################
#
#  Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#  All Rights Reserved
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
'''
This module provides online bank databases for conversion between BBAN and
IBAN numbers and for consulting.
'''
import re
import urllib
import urllib2

from openerp.addons.account_banking_iban_lookup.urlagent import (
    URLAgent,
    SoupForm,
)
from openerp.addons.account_banking.sepa.iban import IBAN
from openerp.addons.account_banking.struct import struct

try:
    import BeautifulSoup
except ImportError:
    BeautifulSoup = None

__all__ = [
    'account_info',
    'bank_info',
]

IBANlink_NL = 'http://www.ibannl.org/iban_check.php'
IBANlink_BE = 'http://www.ibanbic.be/'


def get_iban_bic_NL(bank_acc):
    '''
    Consult the Dutch online banking database to check both the account number
    and the bank to which it belongs. Will not work offline, is limited to
    banks operating in the Netherlands and will only convert Dutch local
    account numbers.
    '''
    # sanity check: Dutch 7 scheme uses ING as sink and online convertor
    # calculates accounts, so no need to consult it - calculate our own
    number = bank_acc.lstrip('0')
    if len(number) <= 7:
        iban = IBAN.create(BBAN='INGB' + number.rjust(10, '0'),
                           countrycode='NL'
                           )
        return struct(
            iban=iban.replace(' ', ''),
            account=iban.BBAN[4:],
            bic='INGBNL2A',
            code='INGBNL',
            bank='ING Bank N.V.',
            country_id='NL',
        )

    data = urllib.urlencode(dict(number=number, method='POST'))
    request = urllib2.Request(IBANlink_NL, data)
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response)
    result = struct()
    attr = None
    for _pass, td in enumerate(soup.findAll('td')):
        if _pass % 2 == 1:
            result[attr] = unicode(td.find('font').contents[0])
        else:
            attr = td.find('strong').contents[0][:4].strip().lower()
    if result:
        result.account = bank_acc
        result.country_id = result.bic[4:6]
        # Nationalized bank code
        result.code = result.bic[:6]
        # All Dutch banks use generic channels
        # result.bic += 'XXX'
        return result
    return None


def get_iban_bic_BE(bank_acc):
    '''
    Consult the Belgian online database to check both account number and the
    bank it belongs to. Will not work offline, is limited to banks operating
    in Belgium and will only convert Belgian local account numbers.
    '''
    def contents(soup, attr):
        return soup.find('input', {
            'id': 'textbox%s' % attr
        }).get('value').strip()

    if not bank_acc.strip():
        return None

    # Get empty form with hidden validators
    agent = URLAgent()
    request = agent.open(IBANlink_BE)

    # Isolate form and fill it in
    soup = BeautifulSoup(request)
    form = SoupForm(soup.find('form', {'id': 'form1'}))
    form['textboxBBAN'] = bank_acc.strip()
    form['Convert'] = 'Convert Number'

    # Submit the form
    response = agent.submit(form)

    # Parse the results
    soup = BeautifulSoup(response)
    iban = contents(soup, 'IBAN')
    if iban.lower().startswith('not a'):
        return None
    result = struct(iban=iban.replace(' ', ''))
    result.bic = contents(soup, 'BIC').replace(' ', '')
    result.bank = contents(soup, 'BankName')

    # Add substracts
    result.account = bank_acc
    result.country_id = result.bic[4:6]
    result.code = result.bic[:6]
    return result


def BBAN_is_IBAN(bank_acc):
    '''
    Intelligent copy, valid for SEPA members who switched to SEPA from old
    standards before SEPA actually started.
    '''
    if isinstance(bank_acc, IBAN):
        iban_acc = bank_acc
    else:
        iban_acc = IBAN(bank_acc)
    return struct(
        iban=str(iban_acc),
        account=str(bank_acc),
        country_id=iban_acc.countrycode,
        code=iban_acc.BIC_searchkey,
        # Note: BIC can not be constructed here!
        bic=False,
        bank=False,
    )


_account_info = {
    # TODO: Add more online data banks
    'BA': BBAN_is_IBAN,
    'BE': get_iban_bic_BE,
    'BG': BBAN_is_IBAN,
    'NL': get_iban_bic_NL,
    'LV': BBAN_is_IBAN,
    'LT': BBAN_is_IBAN,
    'LU': BBAN_is_IBAN,
    'MU': BBAN_is_IBAN,
    'SM': BBAN_is_IBAN,
}


def account_info(iso, bank_acc):
    '''
    Consult the online database for this country to obtain its
    corresponding IBAN/BIC number and other info available.
    Returns None when a service was found but something went wrong.
    Returns a dictionary (struct) of information when found, or
    False when not implemented.
    '''
    if iso in _account_info:
        return _account_info[iso](bank_acc)
    return False


bic_re = re.compile("[^']+'([^']*)'.*")
SWIFTlink = 'http://www.swift.com/bsl/freequery.do'


def bank_info(bic):
    '''
    Consult the free online SWIFT service to obtain the name and address of a
    bank. This call may take several seconds to complete, due to the number of
    requests to make. In total three HTTP requests are made per function call.
    In theory one request could be stripped, but the SWIFT terms of use prevent
    automated usage, so user like behavior is required.

    Update January 2012: Always return None, as the SWIFT page to retrieve the
    information does no longer exist.
    If demand exists, maybe bite the bullet and integrate with a paid web
    service such as http://www.iban-rechner.de.
    lp914922 additionally suggests to make online lookup optional.
    '''

    return None, None
