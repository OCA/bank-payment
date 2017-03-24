# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 credativ Ltd (<http://www.credativ.co.uk>).
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

import datetime
import unittest2 as unittest
from . import paymul

from decimal import Decimal


class PaymulTestCase(unittest.TestCase):

    def setUp(self):
        super(PaymulTestCase, self).setUp()
        self.maxDiff = None

    def test_uk_high_value_priority_payment(self):
        # Changes from spec example: Removed DTM for transaction, HSBC ignores
        # it (section 2.8.3)
        expected = """\
UNB+UNOA:3+::ABC00000001+::HEXAGON ABC+041111:1500+UKHIGHVALUE'
UNH+1+PAYMUL:D:96A:UN:FUN01G'
BGM+452+UKHIGHVALUE+9'
DTM+137:20041111:102'
LIN+1'
DTM+203:20041112:102'
RFF+AEK:UKHIGHVALUE'
MOA+9:1.00:GBP'
FII+OR+12345678:HSBC NET TEST::GBP+:::400515:154:133+GB'
NAD+OY++HSBC BANK PLC:HSBC NET TEST:TEST:TEST:UNITED KINGDOM'
SEQ++1'
MOA+9:1.00:GBP'
RFF+CR:CRUKHV5'
RFF+PQ:PQUKHV5'
PAI+::52:::Z24'
FCA+13'
FII+BF+87654321:XYX LTD FROM FII BF 1:BEN NAME 2:GBP+:::403124:154:133+GB'
NAD+BE++SOME BANK PLC:HSBC NET TEST:TEST:TEST:UNITED KINGDOM'
CNT+39:1'
UNT+19+1'
UNZ+1+UKHIGHVALUE'"""

        src_account = paymul.UKAccount(
            number=12345678,
            holder='HSBC NET TEST',
            currency='GBP',
            sortcode=400515
        )

        dest_account = paymul.UKAccount(
            number=87654321,
            holder="XYX LTD FROM FII BF 1\nBEN NAME 2",
            currency='GBP',
            sortcode=403124
        )

        transaction = paymul.Transaction(
            amount=Decimal('1.00'),
            currency='GBP',
            account=dest_account,
            charges=paymul.CHARGES_PAYEE,
            means=paymul.MEANS_PRIORITY_PAYMENT,
            channel=paymul.CHANNEL_INTRA_COMPANY,
            name_address="SOME BANK PLC\n"
                         "HSBC NET TEST\n"
                         "TEST\n"
                         "TEST\n"
                         "UNITED KINGDOM",
            customer_reference='CRUKHV5',
            payment_reference='PQUKHV5'
        )

        batch = paymul.Batch(
            exec_date=datetime.date(2004, 11, 12),
            reference='UKHIGHVALUE',
            debit_account=src_account,
            name_address="HSBC BANK PLC\n"
                         "HSBC NET TEST\n"
                         "TEST\n"
                         "TEST\n"
                         "UNITED KINGDOM")
        batch.transactions.append(transaction)

        message = paymul.Message(reference='UKHIGHVALUE',
                                 dt=datetime.datetime(2004, 11, 11))
        message.batches.append(batch)

        interchange = paymul.Interchange(
            client_id='ABC00000001',
            reference='UKHIGHVALUE',
            create_dt=datetime.datetime(2004, 11, 11, 15, 00),
            message=message
        )

        self.assertMultiLineEqual(expected, str(interchange))

    def test_ezone(self):
        # Changes from example in spec: Changed CNT from 27 to 39, because we
        # only generate that and it makes no difference which one we use
        # Removed DTM for transaction, HSBC ignores it (section 2.8.3)

        expected = """UNB+UNOA:3+::ABC12016001+::HEXAGON ABC+080110:0856+EZONE'
UNH+1+PAYMUL:D:96A:UN:FUN01G'
BGM+452+EZONE+9'
DTM+137:20080110:102'
LIN+1'
DTM+203:20080114:102'
RFF+AEK:EZONE'
MOA+9:1.00:EUR'
FII+OR+12345678:ACCOUNT HOLDER NAME::EUR+:::403124:154:133+GB'
NAD+OY++ORD PARTY NAME NADOY 01:CRG TC5 001 NADOY ADDRESS LINE 0001:CRG TC5 \
1001 NADOY ADDRESS LINE 0002'
SEQ++1'
MOA+9:1.00:EUR'
RFF+CR:EZONE 1A'
RFF+PQ:EZONE 1A'
PAI+::2'
FCA+14'
FII+BF+DE23300308800099990031:CRG TC5 001 BENE NAME FIIBF \
000001::EUR+AACSDE33:25:5:::+DE'
NAD+BE+++BENE NAME NADBE T1 001:CRG TC5 001T1 NADBE ADD LINE 1 0001:CRG TC5 \
001T1 NADBE ADD LINE 2 0001'
CNT+39:1'
UNT+19+1'
UNZ+1+EZONE'"""

        src_account = paymul.UKAccount(
            number=12345678,
            holder='ACCOUNT HOLDER NAME',
            currency='EUR',
            sortcode=403124
        )

        dest_account = paymul.IBANAccount(
            iban="DE23300308800099990031",
            holder="CRG TC5 001 BENE NAME FIIBF 000001",
            currency='EUR',
            bic="AACSDE33"
        )

        party_name = ("BENE NAME NADBE T1 001\n"
                      "CRG TC5 001T1 NADBE ADD LINE 1 0001\n"
                      "CRG TC5 001T1 NADBE ADD LINE 2 0001")
        transaction = paymul.Transaction(amount=Decimal('1.00'),
                                         currency='EUR',
                                         account=dest_account,
                                         party_name=party_name,
                                         charges=paymul.CHARGES_EACH_OWN,
                                         means=paymul.MEANS_EZONE,
                                         customer_reference='EZONE 1A',
                                         payment_reference='EZONE 1A')

        name_address = ("ORD PARTY NAME NADOY 01\n"
                        "CRG TC5 001 NADOY ADDRESS LINE 0001\n"
                        "CRG TC5 001 NADOY ADDRESS LINE 0002")
        batch = paymul.Batch(exec_date=datetime.date(2008, 1, 14),
                             reference='EZONE',
                             debit_account=src_account,
                             name_address=name_address)
        batch.transactions.append(transaction)

        message = paymul.Message(reference='EZONE',
                                 dt=datetime.datetime(2008, 1, 10))
        message.batches.append(batch)

        interchange = paymul.Interchange(
            client_id='ABC12016001',
            reference='EZONE',
            create_dt=datetime.datetime(2008, 1, 10, 8, 56),
            message=message
        )

        self.assertMultiLineEqual(expected, str(interchange))

    def test_uk_low_value_ach_instruction_level(self):
        dest_account1 = paymul.UKAccount(
            number=87654321,
            holder="HSBC NET RPS TEST\nHSBC BANK",
            currency='GBP',
            sortcode=403124
        )
        name_address = ("HSBC BANK PLC\n"
                        "PCM\n"
                        "8CS37\n"
                        "E14 5HQ\n"
                        "UNITED KINGDOM")
        transaction1 = paymul.Transaction(amount=Decimal('1.00'),
                                          currency='GBP',
                                          account=dest_account1,
                                          name_address=name_address,
                                          charges=paymul.CHARGES_PAYEE,
                                          means=paymul.MEANS_ACH,
                                          customer_reference='CREDIT',
                                          payment_reference='CREDIT')

        dest_account2 = paymul.UKAccount(
            number=12341234,
            holder="HSBC NET RPS TEST\nHSBC BANK",
            currency='GBP',
            sortcode=403124
        )
        name_address = ("HSBC BANK PLC\n"
                        "PCM\n"
                        "8CS37\n"
                        "E14 5HQ\n"
                        "UNITED KINGDOM")
        transaction2 = paymul.Transaction(amount=Decimal('1.00'),
                                          currency='GBP',
                                          account=dest_account2,
                                          name_address=name_address,
                                          charges=paymul.CHARGES_PAYEE,
                                          means=paymul.MEANS_ACH,
                                          customer_reference='CREDIT1',
                                          payment_reference='CREDIT1')

        name_address = ("HSBC BANK PLC\n"
                        "PCM\n"
                        "8CS37\n"
                        "E14 5HQ\n"
                        "UNITED KINGDOM")

        src_account = paymul.UKAccount(number=12345678,
                                       holder='BHEX RPS TEST',
                                       currency='GBP',
                                       sortcode=401234)
        batch = paymul.Batch(exec_date=datetime.date(2004, 11, 15),
                             reference='UKLVPLIL',
                             debit_account=src_account,
                             name_address=name_address)
        batch.transactions = [transaction1, transaction2]

        message = paymul.Message(
            reference='UKLVPLIL',
            dt=datetime.datetime(2004, 11, 11)
        )
        message.batches.append(batch)

        interchange = paymul.Interchange(
            client_id='ABC00000001',
            reference='UKLVPLIL',
            create_dt=datetime.datetime(2004, 11, 11, 15, 0),
            message=message
        )

        # Changes from example:
        # * Change second transaction from EUR to GBP, because we don't support
        #   multi-currency batches
        # * Removed DTM for transaction, HSBC ignores it (section 2.8.3)
        expected = """\
UNB+UNOA:3+::ABC00000001+::HEXAGON ABC+041111:1500+UKLVPLIL'
UNH+1+PAYMUL:D:96A:UN:FUN01G'
BGM+452+UKLVPLIL+9'
DTM+137:20041111:102'
LIN+1'
DTM+203:20041115:102'
RFF+AEK:UKLVPLIL'
MOA+9:2.00:GBP'
FII+OR+12345678:BHEX RPS TEST::GBP+:::401234:154:133+GB'
NAD+OY++HSBC BANK PLC:PCM:8CS37:E14 5HQ:UNITED KINGDOM'
SEQ++1'
MOA+9:1.00:GBP'
RFF+CR:CREDIT'
RFF+PQ:CREDIT'
PAI+::2'
FCA+13'
FII+BF+87654321:HSBC NET RPS TEST:HSBC BANK:GBP+:::403124:154:133+GB'
NAD+BE++HSBC BANK PLC:PCM:8CS37:E14 5HQ:UNITED KINGDOM'
SEQ++2'
MOA+9:1.00:GBP'
RFF+CR:CREDIT1'
RFF+PQ:CREDIT1'
PAI+::2'
FCA+13'
FII+BF+12341234:HSBC NET RPS TEST:HSBC BANK:GBP+:::403124:154:133+GB'
NAD+BE++HSBC BANK PLC:PCM:8CS37:E14 5HQ:UNITED KINGDOM'
CNT+39:2'
UNT+27+1'
UNZ+1+UKLVPLIL'"""

        self.assertMultiLineEqual(expected, str(interchange))


if __name__ == "__main__":
    unittest.main()
