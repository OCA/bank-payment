# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

'''
This module provides a utility class to extract postal codes from address
strings.
'''
import re

__all__ = ['split', 'get', 'PostalCode']


class PostalCode(object):
    '''
    The PostalCode class is a wrapper around PostCodeFormat and an internal
    database of postalcode formats. It provides the class methods split() and
    get(), both of which must be called with the two character iso country
    code as first parameter.
    '''

    class PostalCodeFormat(object):
        '''
        Utility class of PostalCode.
        Allows finding and splitting of postalcode in strings
        '''
        def __init__(self, format):
            '''
            Create regexp patterns for matching
            '''
            # Sort formats on length, longest first
            formats = [(len(x), x) for x in format.split('|')]
            formats = [x[1] for x in sorted(formats, lambda x, y: -cmp(x, y))]
            self.res = [re.compile(x.replace('#', '\\d').replace('@', '[A-Z]'))
                        for x in formats
                        ]

        def get(self, str_):
            '''
            Return the postal code from the string str_
            '''
            for re_ in self.res:
                retval = re_.findall(str_)
                if retval:
                    break
            return retval and retval[0] or ''

        def split(self, str_):
            '''
            Split str_ into (postalcode, remainder)
            '''
            for re_ in self.res:
                pos = re_.search(str_)
                if pos:
                    break
            if pos:
                return (pos.group(), str_[pos.end():])
            return ('', str_)

    _formats = {
        'AF': '', 'AX': '', 'AL': '', 'DZ': '#####', 'AS': '', 'AD': 'AD###',
        'AO': '', 'AI': '', 'AQ': '', 'AG': '', 'AR': '@####@@@',
        'AM': '######', 'AW': '', 'AU': '####', 'AT': '####', 'AZ': 'AZ ####',
        'BS': '', 'BH': '####|###', 'BD': '####', 'BB': 'BB#####',
        'BY': '######', 'BE': '####', 'BZ': '', 'BJ': '', 'BM': '@@ ##',
        'BT': '', 'BO': '', 'BA': '#####', 'BW': '', 'BV': '',
        'BR': '#####-###', 'IO': '', 'BN': '@@####', 'BG': '####', 'BF': '',
        'BI': '', 'KH': '#####', 'CM': '', 'CA': '@#@ #@#', 'CV': '####',
        'KY': '', 'CF': '', 'TD': '', 'CL': '#######', 'CN': '######',
        'CX': '####', 'CC': '', 'CO': '', 'KM': '', 'CG': '', 'CD': '',
        'CK': '', 'CR': '####', 'CI': '', 'HR': 'HR-#####', 'CU': 'CP #####',
        'CY': '####', 'CZ': '### ##', 'DK': '####', 'DJ': '', 'DM': '',
        'DO': '#####', 'EC': '@####@', 'EG': '#####', 'SV': 'CP ####',
        'GQ': '', 'ER': '', 'EE': '#####', 'ET': '####', 'FK': '',
        'FO': 'FO-###', 'FJ': '', 'FI': 'FI-#####', 'FR': '#####',
        'GF': '#####', 'PF': '#####', 'TF': '', 'GA': '', 'GM': '',
        'GE': '####', 'DE': '#####', 'GH': '', 'GI': '', 'GR': '### ##',
        'GL': '####', 'GD': '', 'GP': '#####', 'GU': '969##', 'GT': '#####',
        'GG': '@# #@@|@## #@@|@@# #@@|@@## #@@|@#@ #@@|@@#@ #@@|GIR0AA',
        'GN': '', 'GW': '####', 'GY': '', 'HT': 'HT####', 'HM': '', 'VA': '',
        'HN': '@@####', 'HK': '', 'HU': '####', 'IS': '###', 'IN': '######',
        'ID': '#####', 'IR': '##########', 'IQ': '#####', 'IE': '',
        'IM': '@# #@@|@## #@@|@@# #@@|@@## #@@|@#@ #@@|@@#@ #@@|GIR0AA',
        'IL': '#####', 'IT': '####', 'JM': '', 'JP': '###-####',
        'JE': '@# #@@|@## #@@|@@# #@@|@@## #@@|@#@ #@@|@@#@ #@@|GIR0AA',
        'JO': '#####', 'KZ': '######', 'KE': '#####', 'KI': '',
        'KP': '###-###',
        'KR': 'SEOUL ###-###', 'KW': '#####', 'KG': '######', 'LA': '#####',
        'LV': 'LV-####', 'LB': '#### ####|####', 'LS': '###', 'LR': '####',
        'LY': '', 'LI': '####', 'LT': 'LT-#####', 'LU': '####', 'MO': '',
        'MK': '####', 'MG': '###', 'MW': '', 'MY': '#####', 'MV': '#####',
        'ML': '', 'MT': '@@@ ###|@@@ ##', 'MH': '', 'MQ': '#####', 'MR': '',
        'MU': '', 'YT': '#####', 'MX': '#####', 'FM': '#####', 'MD': 'MD-####',
        'MC': '#####', 'MN': '######', 'ME': '#####', 'MS': '', 'MA': '#####',
        'MZ': '####', 'MM': '#####', 'NA': '', 'NR': '', 'NP': '#####',
        'NL': '#### @@', 'AN': '', 'NC': '#####', 'NZ': '####',
        'NI': '###-###-#', 'NE': '####', 'NG': '######', 'NU': '', 'NF': '',
        'MP': '', 'NO': '####', 'OM': '###', 'PK': '#####', 'PW': '96940',
        'PS': '', 'PA': '', 'PG': '###', 'PY': '####', 'PE': '', 'PH': '####',
        'PN': '', 'PL': '##-###', 'PT': '####-###', 'PR': '#####-####',
        'QA': '', 'RE': '#####', 'RO': '######', 'RU': '######', 'RW': '',
        'BL': '### ###', 'SH': 'STHL 1ZZ', 'KN': '', 'LC': '', 'MF': '### ###',
        'PM': '', 'VC': '', 'WS': '', 'SM': '4789#', 'ST': '', 'SA': '#####',
        'SN': '#####', 'RS': '######', 'SC': '', 'SL': '', 'SG': '######',
        'SK': '###  ##', 'SI': 'SI- ####', 'SB': '', 'SO': '@@  #####',
        'ZA': '####', 'GS': '', 'ES': '#####', 'LK': '#####', 'SD': '#####',
        'SR': '', 'SJ': '', 'SZ': '@###', 'SE': 'SE-### ##', 'CH': '####',
        'SY': '', 'TW': '#####', 'TJ': '######', 'TZ': '', 'TH': '#####',
        'TL': '', 'TG': '', 'TK': '', 'TO': '', 'TT': '', 'TN': '####',
        'TR': '#####', 'TM': '######', 'TC': 'TKCA 1ZZ', 'TV': '', 'UG': '',
        'UA': '#####', 'AE': '',
        'GB': '@# #@@|@## #@@|@@# #@@|@@## #@@|@#@ #@@|@@#@ #@@|GIR0AA',
        'US': '#####-####', 'UM': '', 'UY': '#####', 'UZ': '######', 'VU': '',
        'VE': '####', 'VN': '######', 'VG': '', 'VI': '', 'WF': '', 'EH': '',
        'YE': '', 'ZM': '#####', 'ZW': ''
    }
    for iso, formatstr in _formats.iteritems():
        _formats[iso] = PostalCodeFormat(formatstr)

    @classmethod
    def split(cls, str_, iso=''):
        '''
        Split string <str_> in (postalcode, remainder) following the specs of
        country <iso>.

        Returns iso, postal code and the remaining part of <str_>.

        When iso is filled but postal code remains empty, no postal code could
        be found according to the rules of iso.

        When iso is empty but postal code is not, a proximity match was
        made where multiple hits gave similar results. A postal code is
        likely, but a unique iso code could not be identified.

        When neither iso or postal code are filled, no proximity match could
        be made.
        '''
        if iso in cls._formats:
            return (iso,) + tuple(cls._formats[iso].split(str_))

        # Find optimum (= max length postalcode) when iso code is unknown
        all = {}
        max_l = 0
        for key in cls._formats.iterkeys():
            i, p, c = cls.split(str_, key)
            l = len(p)
            if l > max_l:
                max_l = l
            if l in all:
                all[l].append((i, p, c))
            else:
                all[l] = [(i, p, c)]
        if max_l > 0:
            if len(all[max_l]) > 1:
                return ('',) + all[max_l][0][1:]
            return all[max_l][0]
        return ('', '', str_)

    @classmethod
    def get(cls, iso, str_):
        '''
        Extracts the postal code from str_ following the specs of country
        <iso>.
        '''
        if iso in cls._formats:
            return cls._formats[iso].get(str_)
        return ''

get = PostalCode.get
split = PostalCode.split
