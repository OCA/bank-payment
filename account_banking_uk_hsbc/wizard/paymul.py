# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 credativ Ltd (<http://www.credativ.co.uk>).
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

from account_banking import sepa
from decimal import Decimal
import datetime
import re

def split_account_holder(holder):
    holder_parts = holder.split("\n")

    try:
        line2 = holder_parts[1]
    except IndexError:
        line2 = ''

    return holder_parts[0], line2

"""
The standard says alphanumeric characters, but spaces are also allowed
"""
def edifact_isalnum(s):
    return bool(re.match(r'^[A-Za-z0-9 ]*$', s))

def edifact_digits(val, digits, mindigits=None):
    if mindigits is None:
        mindigits = digits

    pattern = r'^[0-9]{' + str(mindigits) + ',' + str(digits) + r'}$'
    return bool(re.match(pattern, str(val)))

class HasCurrency(object):
    def _get_currency(self):
        return self._currency

    def _set_currency(self, currency):
        if currency is None:
            self._currency = None
        else:
            if not len(currency) <= 3:
                raise ValueError("Currency must be <= 3 characters long: " +
                                 str(currency))
    
            if not edifact_isalnum(currency):
                raise ValueError("Currency must be alphanumeric: " + str(currency))
    
            self._currency = currency.upper()

    currency = property(_get_currency, _set_currency)


class LogicalSection(object):

    def __str__(self):
        segments = self.segments()

        def format_segment(segment):
            return '+'.join([':'.join([str(y) for y in x]) for x in segment]) + "'"

        return "\n".join([format_segment(s) for s in segments])


def _fii_segment(self, party_qualifier):
    holder = split_account_holder(self.holder)
    account_identification = [self.number, holder[0]]
    if holder[1] or self.currency:
        account_identification.append(holder[1])
    if self.currency: 
        account_identification.append(self.currency)
    return [
        ['FII'],
        [party_qualifier],
        account_identification,
        self.institution_identification,
        [self.country],
    ]


class UKAccount(HasCurrency):
    def _get_number(self):
        return self._number

    def _set_number(self, number):
        if not edifact_digits(number, 8):
            raise ValueError("Account number must be 8 digits long: " +
                             str(number))

        self._number = number

    number = property(_get_number, _set_number)

    def _get_sortcode(self):
        return self._sortcode

    def _set_sortcode(self, sortcode):
        if not edifact_digits(sortcode, 6):
            raise ValueError("Account sort code must be 6 digits long: " +
                             str(sortcode))

        self._sortcode = sortcode

    sortcode = property(_get_sortcode, _set_sortcode)

    def _get_holder(self):
        return self._holder

    def _set_holder(self, holder):
        holder_parts = split_account_holder(holder)

        if not len(holder_parts[0]) <= 35:
            raise ValueError("Account holder must be <= 35 characters long")

        if not len(holder_parts[1]) <= 35:
            raise ValueError("Second line of account holder must be <= 35 characters long")

        if not edifact_isalnum(holder_parts[0]):
            raise ValueError("Account holder must be alphanumeric")

        if not edifact_isalnum(holder_parts[1]):
            raise ValueError("Second line of account holder must be alphanumeric")

        self._holder = holder.upper()

    holder = property(_get_holder, _set_holder)

    def __init__(self, number, holder, currency, sortcode):
        self.number = number
        self.holder = holder
        self.currency = currency
        self.sortcode = sortcode
        self.country = 'GB'
        self.institution_identification = ['', '', '', self.sortcode, 154, 133]

    def fii_bf_segment(self):
        return _fii_segment(self, 'BF')

    def fii_or_segment(self):
        return _fii_segment(self, 'OR')

class IBANAccount(HasCurrency):
    def _get_iban(self):
        return self._iban

    def _set_iban(self, iban):
        iban_obj = sepa.IBAN(iban)
        if not iban_obj.valid:
            raise ValueError("IBAN is invalid")

        self._iban = iban
        self.country = iban_obj.countrycode

    iban = property(_get_iban, _set_iban)

    def __init__(self, iban, bic, currency, holder):
        self.iban = iban
        self.number = iban
        self.bic = bic
        self.currency = currency
        self.holder = holder
        self.institution_identification = [self.bic, 25, 5, '', '', '' ]

    def fii_bf_segment(self):
        return _fii_segment(self, 'BF')

class Interchange(LogicalSection):
    def _get_reference(self):
        return self._reference

    def _set_reference(self, reference):
        if not len(reference) <= 15:
            raise ValueError("Reference must be <= 15 characters long")

        if not edifact_isalnum(reference):
            raise ValueError("Reference must be alphanumeric")

        self._reference = reference.upper()

    reference = property(_get_reference, _set_reference)

    def __init__(self, client_id, reference, create_dt=None, message=None):
        self.client_id = client_id
        self.create_dt = create_dt or datetime.datetime.now()
        self.reference = reference
        self.message = message

    def segments(self):
        segments = []
        segments.append([
            ['UNB'],
            ['UNOA', 3],
            ['', '', self.client_id],
            ['', '', 'HEXAGON ABC'],
            [self.create_dt.strftime('%y%m%d'), self.create_dt.strftime('%H%M')],
            [self.reference],
        ])
        segments += self.message.segments()
        segments.append([
            ['UNZ'],
            [1],
            [self.reference],
        ])
        return segments


class Message(LogicalSection):
    def _get_reference(self):
        return self._reference

    def _set_reference(self, reference):
        if not len(reference) <= 35:
            raise ValueError("Reference must be <= 35 characters long")

        if not edifact_isalnum(reference):
            raise ValueError("Reference must be alphanumeric")

        self._reference = reference.upper()

    reference = property(_get_reference, _set_reference)

    def __init__(self, reference, dt=None):
        if dt:
            self.dt = dt
        else:
            self.dt = datetime.datetime.now()

        self.reference = reference
        self.batches = []

    def segments(self):
        # HSBC only accepts one message per interchange
        message_reference_number = 1

        segments = []

        segments.append([
            ['UNH'],
            [message_reference_number],
            ['PAYMUL', 'D', '96A', 'UN', 'FUN01G'],
        ])
        segments.append([
            ['BGM'],
            [452],
            [self.reference],
            [9],
        ])
        segments.append([
            ['DTM'],
            (137, self.dt.strftime('%Y%m%d'), 102),
        ])
        for index, batch in enumerate(self.batches):
            segments += batch.segments(index + 1)
        segments.append([
            ['CNT'],
            ['39', sum([len(x.transactions) for x in self.batches])],
        ])
        segments.append([
            ['UNT'],
            [len(segments) + 1],
            [message_reference_number]
        ])

        return segments

class Batch(LogicalSection):
    def _get_reference(self):
        return self._reference

    def _set_reference(self, reference):
        if not len(reference) <= 18:
            raise ValueError("Reference must be <= 18 characters long")

        if not edifact_isalnum(reference):
            raise ValueError("Reference must be alphanumeric")

        self._reference = reference.upper()

    reference = property(_get_reference, _set_reference)

    def __init__(self, exec_date, reference, debit_account, name_address):
        self.exec_date = exec_date
        self.reference = reference
        self.debit_account = debit_account
        self.name_address = name_address
        self.transactions = []

    def amount(self):
        return sum([x.amount for x in self.transactions])

    def segments(self, index):
        if not edifact_digits(index, 6, 1):
            raise ValueError("Index must be 6 digits or less")

        segments = []

        segments.append([
            ['LIN'],
            [index],
        ])
        segments.append([
            ['DTM'],
            [203, self.exec_date.strftime('%Y%m%d'), 102],
        ])
        segments.append([
            ['RFF'],
            ['AEK', self.reference],
        ])

        currencies = set([x.currency for x in self.transactions])
        if len(currencies) > 1:
            raise ValueError("All transactions in a batch must have the same currency")

        segments.append([
            ['MOA'],
            [9, self.amount().quantize(Decimal('0.00')), currencies.pop()],
        ])
        segments.append(self.debit_account.fii_or_segment())
        segments.append([
            ['NAD'],
            ['OY'],
            [''],
            self.name_address.upper().split("\n")[0:5],
        ])

        for index, transaction in enumerate(self.transactions):
            segments += transaction.segments(index + 1)

        return segments

# From the spec for FCA segments:
# 13 = All charges borne by payee (or beneficiary)
# 14 = Each pay own cost
# 15 = All charges borne by payor (or ordering customer)
# For Faster Payments this should always be ‘14’
# Where this field is not present, “14” will be used as a default.
CHARGES_PAYEE = 13
CHARGES_EACH_OWN = 14
CHARGES_PAYER = 15

MEANS_ACH = 2
MEANS_EZONE = 2
MEANS_PRIORITY_PAYMENT = 52

CHANNEL_INTRA_COMPANY = 'Z24'

class Transaction(LogicalSection, HasCurrency):
    def _get_amount(self):
        return self._amount

    def _set_amount(self, amount):
        if len(str(amount)) > 18:
            raise ValueError("Amount must be shorter than 18 bytes")

        self._amount = amount

    amount = property(_get_amount, _set_amount)

    def _get_payment_reference(self):
        return self._payment_reference

    def _set_payment_reference(self, payment_reference):
        if not len(payment_reference) <= 18:
            raise ValueError("Payment reference must be <= 18 characters long")

        if not edifact_isalnum(payment_reference):
            raise ValueError("Payment reference must be alphanumeric")

        self._payment_reference = payment_reference.upper()

    payment_reference = property(_get_payment_reference, _set_payment_reference)

    def _get_customer_reference(self):
        return self._customer_reference

    def _set_customer_reference(self, customer_reference):
        if not len(customer_reference) <= 18:
            raise ValueError("Customer reference must be <= 18 characters long")

        if not edifact_isalnum(customer_reference):
            raise ValueError("Customer reference must be alphanumeric")

        self._customer_reference = customer_reference.upper()

    customer_reference = property(_get_customer_reference, _set_customer_reference)

    def __init__(self, amount, currency, account, means,
                 name_address=None, party_name=None, channel='',
                 charges=CHARGES_EACH_OWN, customer_reference=None,
                 payment_reference=None):
        self.amount = amount
        self.currency = currency
        self.account = account
        self.name_address = name_address
        self.party_name = party_name
        self.means = means
        self.channel = channel
        self.charges = charges
        self.payment_reference = payment_reference
        self.customer_reference = customer_reference

    def segments(self, index):
        segments = []
        segments.append([
            ['SEQ'],
            [''],
            [index],
        ])
        segments.append([
            ['MOA'],
            [9, self.amount.quantize(Decimal('0.00')), self.currency],
        ])

        if self.customer_reference:
            segments.append([
                ['RFF'],
                ['CR', self.customer_reference],
            ])

        if self.payment_reference:
            segments.append([
                ['RFF'],
                ['PQ', self.payment_reference],
            ])

        if self.channel:
            segments.append([
                ['PAI'],
                ['', '', self.means, '', '', self.channel],
            ])
        else:
            segments.append([
                ['PAI'],
                ['', '', self.means],
            ])

        segments.append([
            ['FCA'],
            [self.charges],
        ])

        segments.append(self.account.fii_bf_segment())

        nad_segment = [
            ['NAD'],
            ['BE'],
            [''],
        ]
        if self.name_address:
            nad_segment.append(self.name_address.upper().split("\n")[0:5])
        else:
            nad_segment.append('')
        if self.party_name:
            nad_segment.append(self.party_name.upper().split("\n")[0:5])
        segments.append(nad_segment)

        return segments
