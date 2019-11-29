# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests
import xmltodict
from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('ippay_ach', 'IPPay ACH eCheck')])
    api_url = fields.Char(
        "Api URL", required_if_provider='ippay_ach')
    ippay_ach_terminal_id = fields.Char(
        "IPpay ACH TerminalID",
        required_if_provider='ippay_ach')


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    @api.model
    def ippay_ach_create(self, values):
        acquirer = self.env['payment.acquirer'].browse(
            values['acquirer_id'])
        check_detail = {'acc_number': values['bank_acc_number'],
                        'aba': values['aba']}
        xml = '''
            <ippay>
                <TransactionType>TOKENIZE</TransactionType>
                <TerminalID>%s</TerminalID>
                <ABA>%s</ABA>
                <AccountNumber>%s</AccountNumber>
            </ippay>''' % (
                acquirer.ippay_ach_terminal_id,
                check_detail.get('aba'),
                check_detail.get('acc_number')
            )
        r = requests.post(
            acquirer.api_url,
            data=xml,
            headers={'Content-Type': 'text/xml'})
        _logger.info("token received: %s" % (r.content))
        data = xmltodict.parse(r.content)
        ippay_response = data.get('IPPayResponse') or data.get('ippayResponse')
        token = ippay_response.get('Token')
        if token:
            return {
                'name': '%s - %s' % (
                    values['bank_acc_number'],
                    values['ch_holder_name']),
                'acquirer_ref': token,
            }
        else:
            raise ValidationError(
                _('Customer payment token creation in'
                  ' IPpay ACH failed: %s - %s%s') % (
                    ippay_response.get('ActionCode'),
                    ippay_response.get('ErrMsg', ''),
                    ippay_response.get('ResponseText', ''),
                ))
