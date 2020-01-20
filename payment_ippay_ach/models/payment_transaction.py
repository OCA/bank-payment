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
    def _ippay_ach_s2s_do_payment(self, invoice):
        sequence = self.acquirer_id.journal_id.sequence_id
        check_number = sequence.next_by_id()
        request = '''
            <ippay>
                <TransactionType>CHECK</TransactionType>
                <TerminalID>%s</TerminalID>
                <CardName>%s</CardName>
                <TotalAmount>%s</TotalAmount>
                <ACH Type = 'SAVINGS' SEC = 'PPD'>
                <Token>%s</Token>
                <CheckNumber>%s</CheckNumber>
                </ACH>
            </ippay>''' % (
                self.acquirer_id.ippay_ach_terminal_id,
                invoice.partner_id.name,
                str(self.amount).replace('.', ''),
                self.payment_token_id.acquirer_ref,
                check_number)
        _logger.info("Request to get IPPay ACH Transaction ID: %s" % (request))
        try:
            r = requests.post(
                self.acquirer_id.api_url,
                data=request,
                headers={'Content-Type': 'text/xml'},
            )
        except Exception as e:
            raise ValidationError(e)
        _logger.info("Transaction Received: %s" % (r.content))

        content = xmltodict.parse(r.content)
        response = content.get('ippayResponse') or content.get('IPPayresponse')
        if (response.get('ResponseText') == 'CHECK ACCEPTED'
                and not response.get('AdditionalInfo')):
            self.acquirer_reference = response.get('TransactionID')
            self.date = fields.Datetime.now()
            self.state = 'done'
        else:
            self.state = 'cancel'
            invoice.message_post(
                body=_("IPPay ACH eCheck Payment DECLINED: %s - %s%s") % (
                    response.get('ActionCode', ''),
                    response.get('ErrMsg', ''),
                    response.get('ResponseText', ''),
                ))

    @api.multi
    def ippay_ach_s2s_do_transaction(self):
        context = self.env.context
        inv_rec = self.env['account.invoice'].browse(context.get('active_ids'))
        for inv in inv_rec:
            if inv.type == 'out_invoice':
                self._ippay_ach_s2s_do_payment(invoice=inv)
