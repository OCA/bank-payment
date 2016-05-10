# -*- coding: utf-8 -*-
# © 2013-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    sepa = fields.Boolean(
        compute='compute_sepa', readonly=True, string="SEPA Payment")
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
    batch_booking = fields.Boolean(
        string='Batch Booking', readonly=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
        track_visibility='onchange',
        help="If true, the bank statement will display only one debit "
        "line for all the wire transfers of the SEPA XML file ; if "
        "false, the bank statement will display one debit line per wire "
        "transfer of the SEPA XML file.")

    @api.multi
    @api.depends(
        'company_partner_bank_id.acc_type',
        'payment_line_ids.currency_id',
        'payment_line_ids.partner_bank_id.acc_type')
    def compute_sepa(self):
        eur = self.env.ref('base.EUR')
        for order in self:
            sepa = True
            if order.company_partner_bank_id.acc_type != 'iban':
                sepa = False
            for pline in order.payment_line_ids:
                if pline.currency_id != eur:
                    sepa = False
                    break
                if pline.partner_bank_id.acc_type != 'iban':
                    sepa = False
                    break
            self.sepa = sepa
