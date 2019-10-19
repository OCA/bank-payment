# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, _
from odoo.exceptions import UserError


class AddCreditCardToken(models.TransientModel):
    _inherit = 'add.credit.card.token'

    @api.multi
    def add_cc_token(self):
        if self.cc_number:
            # Validate the credit card number
            if not self.validate(self.cc_number):
                raise UserError(_(
                    "Error: Not Valid Credit Card Number!"
                ))
        # Search for authorize.net acquirer
        authorize = self.env['payment.acquirer'].search(
            [('provider', '=', 'ippay')])
        if not authorize:
            raise UserError(_(
                "Error: IPpay Needs configuration!"
            ))
        if not self.partner_id.zip or not self.partner_id.street or \
                not self.partner_id.city or not self.partner_id.state_id or \
                not self.partner_id.country_id:
            raise UserError(_(
                "Address Validation: Please verify partner address \
                (street, city, zip, state, country)!"
            ))
        # creating payment token data
        payment_token_data = {
            'acquirer_id': authorize.id,
            'partner_id': self.partner_id.id,
            'cc_number': self.cc_number,
            'cc_expiry_month': self.cc_expiry_month,
            'cc_expiry_year': self.cc_expiry_year,
            'cc_brand': 'visa',
            'cc_cvc': self.cc_cvc,
            'cc_holder_name': self.partner_id.name,
        }
        # create payment token
        self.env['payment.token'].create(payment_token_data)
