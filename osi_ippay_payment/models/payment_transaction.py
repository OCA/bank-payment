# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests
import xmltodict
import json
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentTansaction(models.Model):
    _inherit = 'payment.transaction'

    @api.multi
    def _ippay_s2s_do_payment(self, invoice):
        acquirer = self.acquirer_id
        amount = str(self.amount).replace('.', '')
        token_data = self.env['payment.token'].search([
            ('acquirer_id', '=', acquirer.id),
            ('partner_id', '=', invoice.partner_id.id)])
        request = '''
            <ippay>
                <TransactionType>SALE</TransactionType>
                <TerminalID>%s</TerminalID>
                <Token>%s</Token>
                <TotalAmount>%s</TotalAmount>
            </ippay>''' % (acquirer.ippay_terminal_id, token_data.acquirer_ref,
                           int(amount))
        _logger.info("Request to get IPPay Transaction ID: %s" % (request))
        if acquirer.api_url:
            url = acquirer.api_url
        try:
            r = requests.post(url, data=request, headers={
                'Content-Type': 'text/xml'})
            data = eval(json.dumps(xmltodict.parse(r.content)
                                   ).replace('null', 'False'))
            _logger.info("Transaction Received: %s" % (r.content))
            if data['ippayResponse'].get('ResponseText') == 'APPROVED':
                self.acquirer_reference = data['ippayResponse'].get(
                    'TransactionID')
                self.date = fields.Datetime.now()
                self.state = 'done'
            else:
                self.state = 'cancel'
                invoice.message_post(
                    body="IPpay Payment Confirmation Declined: %s" % (
                        data['ippayResponse'].get('ErrMsg')))
        except Exception as e:
            raise ValidationError(_(e))

    @api.multi
    def ippay_s2s_do_transaction(self):
        context = self.env.context
        inv_rec = self.env['account.invoice'].browse(context.get('active_ids'))
        for inv in inv_rec:
            if inv.type == 'out_invoice':
                self._ippay_s2s_do_payment(invoice=inv)
