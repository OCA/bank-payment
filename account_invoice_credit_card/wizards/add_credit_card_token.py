# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError

BrandNames = {
    '3': 'americanexpress',
    '4': 'visa',
    '5': 'mastercard',
    '6': 'discovercard'
}


class AddCreditCardToken(models.TransientModel):
    _name = 'add.credit.card.token'
    _description = 'Add Credit Card Token'

    cc_number = fields.Char("Card Number", size=16)
    partner_id = fields.Many2one("res.partner", string="Partner")
    cc_expiry_month = fields.Char("Month", size=2)
    cc_expiry_year = fields.Char("Year", size=2)
    cc_cvc = fields.Char("CVC", size=4)
    cc_brand = fields.Char("Brand", default="")
    provider_id = fields.Many2one('payment.acquirer', "Provider")

    @api.onchange('cc_number')
    def onchange_cc_number(self):
        # Check the Card Brand
        if self.cc_number:
            cc_number = self.cc_number
            self.cc_brand = BrandNames.get(cc_number[0])

    def sum_digits(self, digit):
        if digit < 10:
            return digit
        else:
            sum = (digit % 10) + (digit // 10)
            return sum

    # Validate the Credit Card number before save
    # Is valid as per Luhn's algorithm or not
    def validate(self, cc_num):
        # reverse the credit card number
        cc_num = cc_num[::-1]
        # convert to integer
        cc_num = [int(x) for x in cc_num]
        # double every second digit
        doubled_second_digit_list = list()
        digits = list(enumerate(cc_num, start=1))
        for index, digit in digits:
            if index % 2 == 0:
                doubled_second_digit_list.append(digit * 2)
            else:
                doubled_second_digit_list.append(digit)

        # add the digits if any number is more than 9
        doubled_second_digit_list = [self.sum_digits(
            x) for x in doubled_second_digit_list]
        # sum all digits
        sum_of_digits = sum(doubled_second_digit_list)
        # return True or False
        return sum_of_digits % 10 == 0

    @api.multi
    def add_cc_token(self):

        if self.cc_number:
            # Validate the credit card number
            if not self.validate(self.cc_number):
                raise UserError(_(
                    "Error: Not Valid Credit Card Number!"
                ))
        # Search for IPpay acquirer
        if self.provider_id.provider != 'manual':
            provider = self.env['payment.acquirer'].search(
                [('provider', '=', self.provider_id.provider),
                 ])
        else:
            raise UserError(_(
                "Error: %s Needs configuration!" % (self.provider_id.name)
            ))
        if not self.partner_id.zip or not self.partner_id.street or \
                not self.partner_id.city or not self.partner_id.state_id or \
                not self.partner_id.country_id:
            raise UserError(_(
                "Address Validation: Please verify partner address \
                (street, city, zip, state, country)!"
            ))
        # creating payment token data
        expiry = str(self.cc_expiry_month) + '/' + str(self.cc_expiry_year)
        payment_token_data = {
            'acquirer_id': provider.id,
            'partner_id': self.partner_id.id,
            'cc_number': self.cc_number,
            'cc_expiry_month': self.cc_expiry_month,
            'cc_expiry_year': self.cc_expiry_year,
            'cc_expiry': expiry,
            'cc_brand': self.cc_brand,
            'cc_cvc': self.cc_cvc,
            'cc_holder_name': self.partner_id.name,
        }
        # create payment token
        self.env['payment.token'].sudo().create(payment_token_data)
