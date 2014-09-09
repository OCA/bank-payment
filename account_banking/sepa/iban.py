# -*- encoding: utf-8 -*-
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

# The information about SEPA account numbers in this module are collected
# from ISO 13616-1, which can be found at SWIFT's website:
# http://www.swift.com/solutions/messaging/information_products/bic_downloads_documents/pdfs/IBAN_Registry.pdf
#
# This module uses both SEPA and IBAN as seemingly interchangeble terms.
# However, a SEPA account is a bank account in the SEPA zone, which is
# represented by a IBAN number, which is build up from a ISO-693-1 two letter
# country code, two check digits and a BBAN number, representing the
# local/national accounting scheme.
#
# With the exception of Turkey, all countries use the full local adressing
# scheme in the IBAN numbers, making it possible to deduce the BBAN from the
# IBAN. As Turkey uses an additional code in the local scheme which is not
# part of the BBAN, for accounts located in Turkeys banks it is not possible
# to use the BBAN to reconstruct the local account.
#
# WARNING:
# This module contains seemingly enough info to create IBAN's from BBAN's.
# Although many BBAN/IBAN conversions seem algorithmic, there is enough
# deviation to take the warning from SEPA seriously: this is the domain of the
# account owning banks. Don't use it, unless you are prepared to loose your
# money. It is for heuristic validation purposes only.

__all__ = ['IBAN', 'BBAN']


def modulo_97_base10(abuffer):
    '''
    Calculate the modulo 97 value of a string in base10
    '''
    checksum = int(abuffer[0])
    for digit in abuffer[1:]:
        checksum *= 10
        checksum += int(digit)
        checksum %= 97
    return checksum


def base36_to_base10str(abuffer):
    '''
    Convert a base36 string value to a string of base10 digits.
    '''
    result = ''
    for digit in abuffer:
        if digit.isalpha():
            result += str(ord(digit) - 55)
        else:
            result += digit
    return result


class BBANFormat(object):
    '''
    A BBANFormat is an auxilliary class for IBAN. It represents the composition
    of a BBAN number from the different elements in order to translate a
    IBAN number to a localized number. The reverse route, transforming a local
    account to a SEPA account, is the sole responsibility of the banks.
    '''

    def __init__(self, ibanfmt, bbanfmt='%A', nolz=False):
        '''
        Specify the structure of the SEPA account in relation to the local
        account. The XXZZ prefix that all SEPA accounts have is not part of
        the structure in BBANFormat.

        ibanfmt: string of identifiers from position 5 (start = 1):
            A = Account position
            N = Account digit
            B = Bank code digit
            C = Branch code digit
            V = Account check digit
            W = Bank code check digit
            X = Additional check digit (some countries check everything)
            P = Account prefix digit

            The combination of N and A can be used to encode minimum length
            leading-zero-stripped account numbers.

            Example: (NL) 'CCCCAAAAAAAAAA'
                      will convert 'INGB0001234567' into
                      bankcode 'INGB' and account '0001234567'

        bbanfmt: string of placeholders for the local bank account
            %C: bank code
            %B: branch code
            %I: IBAN number (complete)
            %T: account type
            %P: account prefix
            %A: account number. This will include the 'N' placeholder
                positions in the ibanfmt.
            %V, %W, %X: check digits (separate meanings)
            %Z: IBAN check digits (only Poland uses these)
            %%: %
            anything else: literal copy

            Example: (AT): '%A BLZ %C'

        nolz: boolean indicating stripping of leading zeroes in the account
              number. Defaults to False
        '''
        self._iban = ibanfmt
        self._bban = bbanfmt
        self._nolz = nolz

    def __extract__(self, spec, value):
        '''Extract the value based on the spec'''
        i = self._iban.find(spec)
        if i < 0:
            return ''
        result = ''
        j = len(self._iban)
        while i < j and self._iban[i] == spec:
            result += value[i+4]
            i += 1
        return self._nolz and result.lstrip('0') or result

    def bankcode(self, iban):
        '''Return the bankcode'''
        return self.__extract__('B', iban)

    def branchcode(self, iban):
        '''Return the branch code'''
        return self.__extract__('C', iban)

    def account(self, iban):
        '''Return the account number'''
        if self._iban.find('N') >= 0:
            prefix = self.__extract__('N', iban).lstrip('0')
        else:
            prefix = ''
        return prefix + self.__extract__('A', iban)

    def BBAN(self, iban):
        '''
        Format the BBAN part of the IBAN in iban following the local
        addressing scheme. We need the full IBAN in order to be able to use
        the IBAN check digits in it, as Poland needs.
        '''
        res = ''
        i = 0
        while i < len(self._bban):
            if self._bban[i] == '%':
                i += 1
                parm = self._bban[i]
                if parm == 'I':
                    res += unicode(iban)
                elif parm in 'BCDPTVWX':
                    res += self.__extract__(parm, iban)
                elif parm == 'A':
                    res += self.account(iban)
                elif parm == 'S':
                    res += iban
                elif parm == 'Z':
                    # IBAN check digits (Poland)
                    res += iban[2:4]
                elif parm == '%':
                    res += '%'
            else:
                res += self._bban[i]
            i += 1
        return res


class IBAN(str):
    '''
    A IBAN string represents a SEPA bank account number. This class provides
    the interpretation and some validation of such strings.

    Mind that, although there is sufficient reason to comment on the chosen
    approach, we are talking about a transition period of at max. 1 year. Good
    is good enough.
    '''
    BBAN_formats = {
        'AL': BBANFormat('CCBBBBVAAAAAAAAAAAAAAAAAA', '%B%A'),
        'AD': BBANFormat('CCCCBBBBAAAAAAAAAAAA', '%A'),
        'AT': BBANFormat('BBBBBAAAAAAAAAAA', '%A BLZ %B'),
        'BE': BBANFormat('CCCAAAAAAAVV', '%C-%A-%V'),
        'BA': BBANFormat('BBBCCCAAAAAAAA', '%I'),
        'BG': BBANFormat('BBBBCCCCAAAAAAAAAA', '%I'),
        'CH': BBANFormat('CCCCCAAAAAAAAAAAAV', '%C %A', nolz=True),
        'CS': BBANFormat('BBBAAAAAAAAAAAAAVV', '%B-%A-%V'),
        'CY': BBANFormat('BBBCCCCCAAAAAAAAAAAAAAAA', '%B%C%A'),
        'CZ': BBANFormat('BBBBPPPPPPAAAAAAAAAA', '%B-%P/%A'),
        'DE': BBANFormat('BBBBBBBBAAAAAAAAAAV', '%A BLZ %B'),
        'DK': BBANFormat('CCCCAAAAAAAAAV', '%C %A%V'),
        'EE': BBANFormat('BBCCAAAAAAAAAAAV', '%A%V'),
        'ES': BBANFormat('BBBBCCCCWVAAAAAAAAAA', '%B%C%W%V%A'),
        'FI': BBANFormat('CCCCTTAAAAAAAV', '%C%T-%A%V', nolz=True),
        'FR': BBANFormat('BBBBBCCCCCAAAAAAAAAAAVV', '%B %C %A %V'),
        'FO': BBANFormat('BBBBAAAAAAAAAV', '%B %A%V'),
        # Great Brittain uses a special display for the branch code, which we
        # can't honor using the current system. If this appears to be a
        # problem, we can come up with something later.
        'GB': BBANFormat('BBBBCCCCCCAAAAAAAAV', '%C %A'),
        'GI': BBANFormat('BBBBAAAAAAAAAAAAAAA', '%A'),
        'GL': BBANFormat('CCCCAAAAAAAAAV', '%C %A%V'),
        'GR': BBANFormat('BBBCCCCAAAAAAAAAAAAAAAA', '%B-%C-%A', nolz=True),
        'HR': BBANFormat('BBBBBBBAAAAAAAAAA', '%B-%A'),
        'HU': BBANFormat('BBBCCCCXAAAAAAAAAAAAAAAV', '%B%C%X %A%V'),
        'IE': BBANFormat('BBBBCCCCCCAAAAAAAA', '%C %A'),
        'IL': BBANFormat('BBBCCCAAAAAAAAAAAAA', '%C%A'),
        # Iceland uses an extra identification number, split in two on
        # display. Coded here as %P%V.
        'IS': BBANFormat('CCCCTTAAAAAAPPPPPPVVVV', '%C-%T-%A-%P-%V'),
        'IT': BBANFormat('WBBBBBCCCCCAAAAAAAAAAAA', '%W/%B/%C/%A'),
        'LV': BBANFormat('BBBBAAAAAAAAAAAAA', '%I'),
        'LI': BBANFormat('CCCCCAAAAAAAAAAAA', '%C %A', nolz=True),
        'LT': BBANFormat('BBBBBAAAAAAAAAAA', '%I'),
        'LU': BBANFormat('BBBAAAAAAAAAAAAA', '%I'),
        'MC': BBANFormat('BBBBBCCCCCAAAAAAAAAAAVV', '%B %C %A %V'),
        'ME': BBANFormat('CCCAAAAAAAAAAAAAVV', '%C-%A-%V'),
        'MK': BBANFormat('BBBAAAAAAAAAAVV', '%B-%A-%V', nolz=True),
        'MT': BBANFormat('BBBBCCCCCAAAAAAAAAAAAAAAAAA', '%A', nolz=True),
        # Mauritius has an aditional bank identifier, a reserved part and the
        # currency as part of the IBAN encoding. As there is no representation
        # given for the local account in ISO 13616-1 we assume IBAN, which
        # circumvents the BBAN display problem.
        'MU': BBANFormat('BBBBBBCCAAAAAAAAAAAAVVVWWW', '%I'),
        # Netherlands has two different local account schemes: one with and
        # one without check digit (9-scheme and 7-scheme). Luckily most Dutch
        # financial services can keep the two apart without telling, so leave
        # that. Also leave the leading zero issue, as most banks are already
        # converting their local account numbers to BBAN format.
        'NL': BBANFormat('BBBBAAAAAAAAAA', '%A'),
        # Norway seems to split the account number in two on display. For now
        # we leave that. If this appears to be a problem, we can fix it later.
        'NO': BBANFormat('CCCCAAAAAV', '%C.%A%V'),
        'PL': BBANFormat('CCCCCCCCAAAAAAAAAAAAAAAA', '%Z%C %A'),
        'PT': BBANFormat('BBBBCCCCAAAAAAAAAAAVV', '%B.%C.%A.%V'),
        'RO': BBANFormat('BBBBAAAAAAAAAAAAAAAA', '%A'),
        'SA': BBANFormat('BBAAAAAAAAAAAAAAAA', '%B%A'),
        'SE': BBANFormat('CCCAAAAAAAAAAAAAAAAV', '%A'),
        'SI': BBANFormat('CCCCCAAAAAAAAVV', '%C-%A%V', ),
        # Slovakia uses two different format for local display. We stick with
        # their formal BBAN specs
        'SK': BBANFormat('BBBBPPPPPPAAAAAAAAAAAA', '%B%P%A'),
        # San Marino: No information for display of BBAN, so stick with IBAN
        'SM': BBANFormat('WBBBBBCCCCCCAAAAAAAAAAAAV', '%I'),
        'TN': BBANFormat('BBCCCAAAAAAAAAAAAAVV', '%B %C %A %V'),
        # Turkey has insufficient information in the IBAN number to regenerate
        # the BBAN: the branch code for local addressing is missing (5n).
        'TR': BBANFormat('BBBBBWAAAAAAAAAAAAAAAA', '%B%C%A'),
    }
    countries = BBAN_formats.keys()
    unknown_BBAN_format = BBANFormat('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', '%I')

    def __new__(cls, arg, **kwargs):
        '''
        All letters should be uppercase and acceptable. As str is an
        in 'C' implemented class, this can't be done in __init__.
        '''
        init = ''
        if arg:
            for item in arg.upper():
                if item.isalnum():
                    init += item
                elif item not in ' \t.-':
                    raise ValueError('Invalid chars found in IBAN number')
        return str.__new__(cls, init)

    def __init__(self, *args, **kwargs):
        '''
        Sanity check: don't offer extensions unless the base is sound.
        '''
        super(IBAN, self).__init__()
        if self.countrycode not in self.countries:
            self.BBAN_format = self.unknown_BBAN_format
        else:
            self.BBAN_format = self.BBAN_formats[self.countrycode]

    @classmethod
    def create(cls, BIC=None, countrycode=None, BBAN=None, bankcode=None,
               branchcode=None, account=None):
        '''
        Create a IBAN number from a BBAN and a country code. Optionaly create
        a BBAN from BBAN components before generation.

        Incomplete: can only work with valid BBAN now.
        '''
        if BIC:
            if not bankcode:
                bankcode = BIC[:4]
            if not countrycode:
                countrycode = BIC[4:6]
        else:
            if countrycode:
                countrycode = countrycode.upper()
            else:
                raise ValueError('Either BIC or countrycode is required')

        if countrycode not in cls.countries:
            raise ValueError('%s is not a SEPA country' % countrycode)
        format = cls.BBAN_formats[countrycode]

        if BBAN:
            if len(BBAN) == len(format._iban):
                ibanno = cls(countrycode + '00' + BBAN)
                return cls(countrycode + ibanno.checksum + BBAN)
            raise ValueError('Insufficient data to generate IBAN')

    @property
    def valid(self):
        '''
        Check if the string + check digits deliver a valid checksum
        '''
        _buffer = self[4:] + self[:4]
        return (
            self.countrycode in self.countries
            and int(base36_to_base10str(_buffer)) % 97 == 1
        )

    def __repr__(self):
        '''
        Formal representation is in chops of four characters, devided by a
        space.
        '''
        parts = []
        for i in range(0, len(self), 4):
            parts.append(self[i:i+4])
        return ' '.join(parts)

    def __unicode__(self):
        '''
        Return unicode representation of self
        '''
        return u'%r' % self

    @property
    def checksum(self):
        '''
        Generate a new checksum for an otherwise correct layed out BBAN in a
        IBAN string.
        NOTE: This is the responsability of the banks. No guaranties whatsoever
        that this delivers usable IBAN accounts. Mind your money!
        '''
        _buffer = self[4:] + self[:2] + '00'
        _buffer = base36_to_base10str(_buffer)
        return '%.2d' % (98 - modulo_97_base10(_buffer))

    @property
    def checkdigits(self):
        '''
        Return the digits which form the checksum in the IBAN string
        '''
        return self[2:4]

    @property
    def countrycode(self):
        '''
        Return the ISO country code
        '''
        return self[:2]

    @property
    def bankcode(self):
        '''
        Return the bank code
        '''
        return self.BBAN_format.bankcode(self)

    @property
    def BIC_searchkey(self):
        '''
        BIC's, or Bank Identification Numbers, are composed of the bank
        code, followed by the country code, followed by the localization
        code, followed by an optional department number.

        The bank code seems to be world wide unique. Knowing this,
        one can use the country + bankcode info from BIC to narrow a
        search for the bank itself.

        Note that some countries use one single localization code for
        all bank transactions in that country, while others do not. This
        makes it impossible to use an algorithmic approach for generating
        the full BIC.
        '''
        return self.bankcode[:4] + self.countrycode

    @property
    def branchcode(self):
        '''
        Return the branch code
        '''
        return self.BBAN_format.branchcode(self)

    @property
    def localized_BBAN(self):
        '''
        Localized format of local or Basic Bank Account Number, aka BBAN
        '''
        if self.countrycode == 'TR':
            # The Turkish BBAN requires information that is not in the
            # IBAN number.
            return False
        return self.BBAN_format.BBAN(self)

    @property
    def BBAN(self):
        '''
        Return full encoded BBAN, which is for all countries the IBAN string
        after the ISO-639 code and the two check digits.
        '''
        return self[4:]


class BBAN(object):
    '''
    Class to reformat a local BBAN account number to IBAN specs.
    Simple validation based on length of spec string elements and real data.
    '''

    @staticmethod
    def _get_length(fmt, element):
        '''
        Internal method to calculate the length of a parameter in a
        formatted string
        '''
        i = 0
        max_i = len(fmt._iban)
        while i < max_i:
            if fmt._iban[i] == element:
                next = i + 1
                while next < max_i and fmt._iban[next] == element:
                    next += 1
                return next - i
            i += 1
        return 0

    def __init__(self, bban, countrycode):
        '''
        Reformat and sanity check on BBAN format.
        Note that this is not a fail safe check, it merely checks the format of
        the BBAN following the IBAN specifications.
        '''
        self._bban = None
        if countrycode.upper() in IBAN.countries:
            self._fmt = IBAN.BBAN_formats[countrycode.upper()]
            res = ''
            i = 0
            j = 0
            max_i = len(self._fmt._bban)
            max_j = len(bban)
            while i < max_i and j < max_j:
                while bban[j] in ' \t' and j < max_j:
                    j += 1
                if self._fmt._bban[i] == '%':
                    i += 1
                    parm = self._fmt._bban[i]
                    if parm == 'I':
                        _bban = IBAN(bban)
                        if _bban.valid:
                            self._bban = str(_bban)
                        else:
                            self._bban = None
                        # Valid, so nothing else to do
                        return
                    elif parm in 'ABCDPSTVWXZ':
                        _len = self._get_length(self._fmt, parm)
                        addon = bban[j:j+_len]
                        if len(addon) != _len:
                            # Note that many accounts in the IBAN standard
                            # are allowed to have leading zeros, so zfill
                            # to full spec length for visual validation.
                            #
                            # Note 2: this may look funny to some, as most
                            # local schemes strip leading zeros. It allows
                            # us however to present the user a visual feedback
                            # in order to catch simple user mistakes as
                            # missing digits.
                            if parm == 'A':
                                res += addon.zfill(_len)
                            else:
                                # Invalid, just drop the work and leave
                                return
                        else:
                            res += addon
                        j += _len
                elif self._fmt._bban[i] in [bban[j], ' ', '/', '-', '.']:
                    res += self._fmt._bban[i]
                    if self._fmt._bban[i] == bban[j]:
                        j += 1
                elif self._fmt._bban[i].isalpha():
                    res += self._fmt._bban[i]
                i += 1
            if i == max_i:
                self._bban = res

    def __str__(self):
        '''String representation'''
        return self._bban

    def __unicode__(self):
        '''Unicode representation'''
        return unicode(self._bban)

    @property
    def valid(self):
        '''Simple check if BBAN is in the right format'''
        return self._bban and True or False


if __name__ == '__main__':
    import sys
    for arg in sys.argv[1:]:
        iban = IBAN(arg)
        print('IBAN:', iban)
        print('country code:', iban.countrycode)
        print('bank code:', iban.bankcode)
        print('branch code:', iban.branchcode)
        print('BBAN:', iban.BBAN)
        print('localized BBAN:', iban.localized_BBAN)
        print('check digits:', iban.checkdigits)
        print('checksum:', iban.checksum)
