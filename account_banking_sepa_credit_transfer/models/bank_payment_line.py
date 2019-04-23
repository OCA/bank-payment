# © braintec-group.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    @api.multi
    @api.depends(
        'order_id.company_partner_bank_id.acc_type',
        'currency_id',
        'partner_bank_id.acc_type')
    def _compute_sepa(self):
        eur = self.env.ref('base.EUR')
        for bank_payment_line in self:
            sepa = True
            if bank_payment_line.order_id.company_partner_bank_id.acc_type != \
                    'iban':
                sepa = False
            elif bank_payment_line.currency_id != eur:
                sepa = False
            elif bank_payment_line.partner_bank_id.acc_type != 'iban':
                sepa = False
            bank_payment_line.sepa = sepa

    sepa = fields.Boolean(
        compute='_compute_sepa', readonly=True, string="SEPA Payment")
