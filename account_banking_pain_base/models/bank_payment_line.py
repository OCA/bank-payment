# © 2013-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    priority = fields.Selection(
        related='payment_line_ids.priority', string='Priority')
    local_instrument = fields.Selection(
        related='payment_line_ids.local_instrument',
        string='Local Instrument')
    category_purpose = fields.Selection(
        related='payment_line_ids.category_purpose', string='Category Purpose')
    purpose = fields.Selection(
        related='payment_line_ids.purpose')
    sepa = fields.Boolean(
        compute='compute_sepa', readonly=True, string="SEPA Payment Line")
    charge_bearer = fields.Selection([
        ('SLEV', 'Following Service Level'),
        ('SHAR', 'Shared'),
        ('CRED', 'Borne by Creditor'),
        ('DEBT', 'Borne by Debtor')], string='Charge Bearer',
        default='SLEV', readonly=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
        track_visibility='onchange',
        help="Following service level : transaction charges are to be "
             "applied following the rules agreed in the service level "
             "and/or scheme (SEPA Core messages must use this). Shared : "
             "transaction charges on the debtor side are to be borne by "
             "the debtor, transaction charges on the creditor side are to "
             "be borne by the creditor. Borne by creditor : all "
             "transaction charges are to be borne by the creditor. Borne "
             "by debtor : all transaction charges are to be borne by the "
             "debtor.")

    @api.model
    def same_fields_payment_line_and_bank_payment_line(self):
        res = super(BankPaymentLine, self).\
            same_fields_payment_line_and_bank_payment_line()
        res += ['priority', 'local_instrument', 'category_purpose', 'purpose',
                'sepa', 'charge_bearer']
        return res

    def compute_sepa(self):
        for bpline in self:
            bpline._compute_sepa_line()

    def _compute_sepa_line(self):
        self.ensure_one()
        eur = self.env.ref('base.EUR')
        self.sepa = True
        if self.currency_id != eur:
            self.sepa = False
        if self.partner_bank_id.acc_type != 'iban':
            self.sepa = False
