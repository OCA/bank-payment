# -*- encoding: utf-8 -*-
##############################################################################
#
#  Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#  All Rights Reserved
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
'''
This module provides online bank databases for conversion between BBAN and
IBAN numbers and for consulting.
'''
import re
import urllib, urllib2
from BeautifulSoup import BeautifulSoup
from account_banking.sepa import postalcode
from account_banking.sepa.urlagent import URLAgent, SoupForm
from account_banking.sepa.iban import IBAN
from account_banking.struct import struct

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
            iban = iban.replace(' ',''),
            account = iban.BBAN[4:],
            bic = 'INGBNL2A',
            code = 'INGBNL',
            bank = 'ING Bank N.V.',
            country_id = 'NL',
        )

    data = urllib.urlencode(dict(number=number, method='POST'))
    request = urllib2.Request(IBANlink_NL, data)
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response)
    result = struct()
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
        return soup.find('input', {'id': 'textbox%s' % attr}).get('value').strip()

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
        iban = str(iban_acc),
        account = str(bank_acc),
        country_id = iban_acc.countrycode,
        code = iban_acc.BIC_searchkey,
        # Note: BIC can not be constructed here!
        bic = False,
        bank = False,
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
    Raise NotImplemented when no information service could be found.
    Returns None when a service was found but something went wrong.
    Returns a dictionary (struct) of information when found.
    '''
    if iso in _account_info:
        return _account_info[iso](bank_acc)
    raise NotImplementedError()

bic_re = re.compile("[^']+'([^']*)'.*")
SWIFTlink = 'http://www.swift.com/bsl/freequery.do'

def bank_info(bic):
    '''
    Consult the free online SWIFT service to obtain the name and address of a
    bank. This call may take several seconds to complete, due to the number of
    requests to make. In total three HTTP requests are made per function call.
    In theory one request could be stripped, but the SWIFT terms of use prevent
    automated usage, so user like behavior is required.
    '''
    def harvest(soup):
        retval = struct()
        for trsoup in soup('tr'):
            for stage, tdsoup in enumerate(trsoup('td')):
                if stage == 0:
                    attr = tdsoup.contents[0].strip().replace(' ','_')
                elif stage == 2:
                    if tdsoup.contents:
                        retval[attr] = tdsoup.contents[0].strip()
                    else:
                        retval[attr] = ''
        return retval

    # Get form
    agent = URLAgent()
    request = agent.open(SWIFTlink)
    soup = BeautifulSoup(request)

    # Parse request form. As this form is intertwined with a table, use the parent
    # as root to search for form elements.
    form = SoupForm(soup.find('form', {'id': 'frmFreeSearch1'}), parent=True)

    # Fill form fields
    form['selected_bic'] = bic

    # Get intermediate response
    response = agent.submit(form)

    # Parse response
    soup = BeautifulSoup(response)

    # Isolate the full 11 BIC - there may be more, but we only use the first
    bic_button = soup.find('a', {'class': 'bigbuttonblack'})
    if not bic_button:
        return None, None

    # Overwrite the location with 'any' ('XXX') to narrow the results to one or less.
    # Assume this regexp will never fail...
    full_bic = bic_re.match(bic_button.get('href')).groups()[0][:8] + 'XXX'

    # Get the detail form
    form = SoupForm(soup.find('form', {'id': 'frmDetail'}))

    # Fill detail fields
    form['selected_bic11'] = full_bic

    # Get final response
    response = agent.submit(form)
    soup = BeautifulSoup(response)

    # Now parse the results
    tables = soup.find('div', {'id':'Middle'}).findAll('table')
    if not tables:
        return None, None
    tablesoup = tables[2]('table')
    if not tablesoup:
        return None, None
    
    codes = harvest(tablesoup[0])
    if not codes:
        return None, None

    bankinfo = struct(
        # Most banks use the first four chars of the BIC as an identifier for
        # their 'virtual bank' accross the world, containing all national
        # banks world wide using the same name.
        # The concatenation with the two character country code is for most
        # national branches sufficient as a unique identifier.
        code = full_bic[:6],
        bic = full_bic,
        name = codes.Institution_name,
    )

    address = harvest(tablesoup[1])
    # The address in the SWIFT database includes a postal code.
    # We need to split it into two fields...
    if not address.Zip_Code:
        if address.Location:
            iso, address.Zip_Code, address.Location = \
                    postalcode.split(address.Location, full_bic[4:6])

    bankaddress = struct(
        street = address.Address.title(),
        city = address.Location.strip().title(),
        zip = address.Zip_Code,
        country = address.Country.title(),
        country_id = full_bic[4:6],
    )
    if '  ' in bankaddress.street:
        bankaddress.street, bankaddress.street2 = [
            x.strip() for x in bankaddress.street.split('  ', 1)
        ]
    else:
        bankaddress.street2 = ''

    return bankinfo, bankaddress

