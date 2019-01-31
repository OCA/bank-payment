# -*- coding: utf-8 -*-
# Copyright 2018 Braintec (https://www.braintec-group.com/)
# @author: Timka Piric Muratovic, Tobias Bächle
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class ResBank(models.Model):
    _inherit = 'res.bank'

    @api.multi
    @api.constrains('csmi_number')
    def check_csmi_number(self):
        for bank in self:
            if not bank.csmi_number:
                continue
            if bank.csmi == 'ATBLZ' and not re.search(r'^[0-9]{5,5}$',
                                                      bank.csmi_number):
                error_msg = _("A valid Austrian Bankleitzahl should contain 5 "
                              "digits. Please enter a correct Clearing System "
                              "Member Identification Number.")
                raise ValidationError(error_msg)
            if bank.csmi == 'AUBSB' and not re.search(r'^[0-9]{6,6}$',
                                                      bank.csmi_number):
                error_message = _("A valid Australian Bank State Branch Code "
                                  "(BSB) contains 6 digits. Please enter a "
                                  "correct Clearing System Member "
                                  "Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'CACPA' and not re.search(r'^[0-9]{9,9}$',
                                                      bank.csmi_number):
                error_message = _("A valid Canadian Payments Association "
                                  "Payment Routing Number contains 9 digits. "
                                  "Please enter a correct Clearing System "
                                  "Member Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'CHBCC' and not re.search(r'^[0-9]{3,5}$',
                                                      bank.csmi_number):
                error_message = _("A valid Swiss Financial Institution "
                                  "Identification (short) contains 3 to 5 "
                                  "digits. Please enter a correct Clearing "
                                  "System Member Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'CHSIC' and not re.search(r'^[0-9]{6,6}$',
                                                      bank.csmi_number):
                error_message = _("A valid Swiss Financial Institution "
                                  "Identification (long) contains 6 digits. "
                                  "Please enter a correct Clearing System "
                                  "Member Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'CNAPS' and not re.search(r'^[0-9]{12,12}$',
                                                      bank.csmi_number):
                error_message = _("A valid CNAPS Identifier contains 12 "
                                  "digits. Please enter a correct Clearing "
                                  "System Member Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'DEBLZ' and not re.search(r'^[0-9]{8,8}$',
                                                      bank.csmi_number):
                error_message = _("A valid German Bankleitzahl contains 8 "
                                  "digits. Please enter a correct Clearing "
                                  "System Member Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'ESNCC' and not re.search(r'^[0-9]{8,9}$',
                                                      bank.csmi_number):
                error_message = _("A valid Spanish Domestic Interbanking Code "
                                  "contains 8 to 9 digits. Please enter a "
                                  "correct Clearing System Member "
                                  "Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'GBDSC' and not re.search(r'^[0-9]{6,6}$',
                                                      bank.csmi_number):
                error_message = _("A valid UK Domestic Sort Code contains 6 "
                                  "digits. Please enter a correct Clearing "
                                  "System Member Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'GRBIC' and not re.search(r'^[0-9]{7,7}$',
                                                      bank.csmi_number):
                error_message = _("A valid Helenic Bank Identification Code "
                                  "contains 7 digits. Please enter a correct "
                                  "Clearing System Member Identification "
                                  "Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'HKNCC' and not re.search(r'^[0-9]{3,3}$',
                                                      bank.csmi_number):
                error_message = _("A valid Hong Kong Bank Code contains 3 "
                                  "digits. Please enter a correct Clearing "
                                  "System Member Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'IENCC' and not re.search(r'^[0-9]{6,6}$',
                                                      bank.csmi_number):
                error_message = _("A valid Irish National Clearing Code "
                                  "contains 6 digits. Please enter a correct "
                                  "Clearing System Member Identification "
                                  "Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'INFSC' and not re.search(r'^[a-zA-Z0-9]{11,11}$',
                                                      bank.csmi_number):
                error_message = _("A valid Indian Financial System Code "
                                  "contains 11 characters. Please enter a "
                                  "correct Clearing System Member "
                                  "Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'ITNCC' and not re.search(r'^[0-9]{10,10}$',
                                                      bank.csmi_number):
                error_message = _("A valid Italian Domestic Identification "
                                  "Code contains 10 digits. Please enter a "
                                  "correct Clearing System Member "
                                  "Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'JPZGN' and not re.search(r'^[0-9]{7,7}$',
                                                      bank.csmi_number):
                error_message = _("A valid Japan Zengin Clearing Code "
                                  "contains 7 digits. Please enter a correct "
                                  "Clearing System Member Identification "
                                  "Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'NZNCC' and not re.search(r'^[0-9]{6,6}$',
                                                      bank.csmi_number):
                error_message = _("A valid New Zealand National Clearing Code "
                                  "contains 6 digits. Please enter a correct "
                                  "Clearing System Member Identification "
                                  "Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'PLKNR' and not re.search(r'^[0-9]{8,8}$',
                                                      bank.csmi_number):
                error_message = _("A valid Polish National Clearing Code "
                                  "contains 8 digits. Please enter a correct "
                                  "Clearing System Member Identification "
                                  "Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'PTNCC' and not re.search(r'^[0-9]{8,8}$',
                                                      bank.csmi_number):
                error_message = _("A valid Portuguese National Clearing Code "
                                  "contains 8 digits. Please enter a correct "
                                  "Clearing System Member Identification "
                                  "Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'RUCBC' and not re.search(r'^[0-9]{9,9}$',
                                                      bank.csmi_number):
                error_message = _("A valid Russian Central Bank "
                                  "Identification Code contains 9 digits. "
                                  "Please enter a correct Clearing System "
                                  "Member Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'SESBA' and not re.search(r'^[0-9]{4,4}$',
                                                      bank.csmi_number):
                error_message = _("A valid Sweden Bankgiro Clearing Code "
                                  "contains 4 digits. Please enter a correct "
                                  "Clearing System Member Identification "
                                  "Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'SGIBG' and not (re.search(r'^[0-9]{7,7}$',
                                                       bank.csmi_number) or
                                             re.search(r'^[0-9]{3,4}$',
                                                       bank.csmi_number)):
                error_message = _("A valid IBG Sort Code contains 3, 4 or 7 "
                                  "digits. Please enter a correct Clearing "
                                  "System Member Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'THCBC' and not re.search(r'^[0-9]{3,3}$',
                                                      bank.csmi_number):
                error_message = _("A valid Thai Central Bank Identification "
                                  "Code contains 3 digits. Please enter a "
                                  "correct Clearing System Member "
                                  "Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'TWNCC' and not re.search(r'^[0-9]{7,7}$',
                                                      bank.csmi_number):
                error_message = _("A valid Financial Institution Code in "
                                  "Taiwan contains 7 digits. Please enter a "
                                  "correct Clearing System Member "
                                  "Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'USABA' and not re.search(r'^[0-9]{9,9}$',
                                                      bank.csmi_number):
                error_message = _("A valid United States Routing Number "
                                  "(Fedwire, NACHA) contains 9 digits. Please "
                                  "enter a correct Clearing System Member "
                                  "Identification Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'USPID' and not re.search(r'^[0-9]{4,4}$',
                                                      bank.csmi_number):
                error_message = _("A valid CHIPS Participant Identifier "
                                  "contains 4 digits. Please enter a correct "
                                  "Clearing System Member Identification "
                                  "Number.")
                raise ValidationError(error_message)
            if bank.csmi == 'ZANCC' and not re.search(r'^[0-9]{6,6}$',
                                                      bank.csmi_number):
                error_message = _("A valid South African National Clearing "
                                  "Code contains 6 digits. Please enter a "
                                  "correct Clearing System Member "
                                  "Identification Number.")
                raise ValidationError(error_message)
        return True

    csmi = fields.Selection(
        [('other', _('Other Financial Institutions')),
         ('ATBLZ', _('Austrian Bankleitzahl - Bank Branch code used in '
                     'Austria')),
         ('AUBSB', _('Australian Bank State Branch Code (BSB) - Bank Branch '
                     'code used in Australia')),
         ('CACPA', _('Canadian Payments Association Payment Routing Number - '
                     'Bank Branch code used in Canada')),
         ('CHBCC', _(
             'Swiss Financial Institution Identification (short) - '
             'Financial Institution Identification (IID) used in Switzerland, '
             'without check digit')),
         ('CHSIC', _(
             'Swiss Financial Institution Identification (long) - '
             'Financial Institution Identification (IID) used in Switzerland, '
             'including check digit')),
         ('CNAPS', _('CNAPS Identifier - Bank Branch code used in China')),
         ('DEBLZ', _('German Bankleitzahl - Bank Branch code used in '
                     'Germany')),
         ('ESNCC', _('Spanish Domestic Interbanking Code - Bank Branch code '
                     'used in Spain')),
         ('GBDSC', _('UK Domestic Sort Code - Bank Branch code used in '
                     'the UK')),
         ('GRBIC', _('Helenic Bank Identification Code - Bank Branch code '
                     'used in Greece')),
         ('HKNCC', _('Hong Kong Bank Code - Bank Branch code used in '
                     'Hong Kong')),
         ('IENCC', _('Irish National Clearing Code - Bank Branch code used '
                     'in Ireland')),
         ('INFSC', _('Indian Financial System Code - Bank Branch code used '
                     'in India')),
         ('ITNCC', _('Italian Domestic Identification Code - Bank Branch '
                     'code used in Italy')),
         ('JPZGN', _('Japan Zengin Clearing Code - Bank Branch code used '
                     'in Japan')),
         ('NZNCC', _('New Zealand National Clearing Code - Bank Branch code '
                     'used in New Zealand')),
         ('PLKNR', _('Polish National Clearing Code - Bank Branch code used '
                     'in Poland')),
         ('PTNCC', _('Portuguese National Clearing Code - Bank Branch code '
                     'used in Portugal')),
         ('RUCBC', _('Russian Central Bank Identification Code - Bank Branch '
                     'code used in Russia')),
         ('SESBA', _('Sweden Bankgiro Clearing Code - Bank Branch code used '
                     'in Sweden')),
         ('SGIBG', _('IBG Sort Code - Bank Branch code used in Singapore')),
         ('THCBC', _('Thai Central Bank Identification Code - '
                     'Bank Identification code used in Thailand')),
         ('TWNCC', _('Financial Institution Code - Bank Branch code used '
                     'in Taiwan')),
         ('USABA', _(
             'United States Routing Number (Fedwire, NACHA) - '
             'Routing Transit number assigned by the ABA for '
             'US financial institutons')),
         ('USPID', _('CHIPS Participant Identifier - Bank identifier used '
                     'by CHIPs in the US')),
         ('ZANCC', _('South African National Clearing Code - '
                     'Bank Branch code used in South Africa'))
         ],
        string='Clearing System Member Identification',
        default='other',
        required=True,
        translate=True,
        help="Clearing System Member Identification - Not all Financial "
             "Institutions have BIC. To do ISO 20022 payments to the banks "
             "without BIC the Clearing System Member Identification"
             " has to be specified.")

    csmi_number = fields.Char(
        string='Clearing System Member Identification Number',
        size=12,
        required=False,
        help="If Clearing System Member Identification is different to "
             "'Other Financial Institutions', Clearing System Member "
             "Identification Number has to be set.")
