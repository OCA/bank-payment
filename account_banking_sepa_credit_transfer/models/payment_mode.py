# -*- coding: utf-8 -*-
# © 2016 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class PaymentMode(models.Model):
    _inherit = 'payment.mode'

    def _sepa_type_get(self):
        res = super(PaymentMode, self)._sepa_type_get()
        if not res:
            if self.type.code and self.type.code.startswith('pain.001'):
                res = 'sepa_credit_transfer'
        return res

    sepa_category_purpose = fields.Selection([
        ('CORT', "[CORT] Transaction is related to settlement of a trade, "
            "eg a foreign exchange deal or a securities transaction."),
        ('SALA', "[SALA] Transaction is the payment of salaries."),
        ('TREA', "[TREA] Transaction is related to treasury operations. "
            "E.g. financial contract settlement."),
        ('CASH', "[CASH] Transaction is a general cash management "
            "instruction."),
        ('DIVI', "[DIVI] Transaction is the payment of dividends."),
        ('GOVT', "[GOVT] Transaction is a payment to or from a "
            "government department."),
        ('INTE', "[INTE] Transaction is the payment of interest."),
        ('LOAN', "[LOAN] Transaction is related to the transfer of "
            "a loan to a borrower."),
        ('PENS', "[PENS] Transaction is the payment of pension."),
        ('SECU', "[SECU] Transaction is the payment of securities."),
        ('SUPP', "[SUPP] Transaction is related to a payment to a supplier."),
        ('SSBE', "[SSBE] Transaction is a social security benefit, ie payment "
            "made by a government to support individuals."),
        ('TAXS', "[TAXS] Transaction is the payment of taxes."),
        ('TRAD', "[TRAD] Transaction is related to the payment of a trade "
            "finance transaction."),
        ('VATX', "[VATX] Transaction is the payment of value added tax."),
        ('HEDG', "[HEDG] Transaction is related to the payment of a hedging "
            "operation."),
        ('INTC', "[INTC] Transaction is an intra-company payment, ie, a "
            "payment between two companies belonging to the same group."),
        ('WHLD', "[WHLD] Transaction is the payment of withholding tax."),
    ], string='SEPA Category Purpose Type', required=False, size=4,
        help="Select the appropiate SEPA category for transactions made "
        "under this payment type. Only appplicable for SEPA Credit Transfers.")
