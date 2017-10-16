# © 2013-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'

    priority = fields.Selection([
        ('NORM', 'Normal'),
        ('HIGH', 'High')],
        string='Priority', default='NORM',
        help="This field will be used as 'Instruction Priority' in "
             "the generated PAIN file.")
    # local_instrument is used for instant credit transfers which
    # will begin on November 2017, cf account_banking_sepa_credit_transfer
    # It is also used in some countries such as switzerland,
    # cf l10n_ch_pain_base that adds some entries in the selection field
    local_instrument = fields.Selection([], string='Local Instrument')
    category_purpose = fields.Selection([
        # Full category purpose list found on:
        # https://www.iso20022.org/external_code_list.page
        # Document "External Code Sets spreadsheet" version Feb 8th 2017
        ('BONU', 'Bonus Payment'),
        ('CASH', 'Cash Management Transfer'),
        ('CBLK', 'Card Bulk Clearing'),
        ('CCRD', 'Credit Card Payment'),
        ('CORT', 'Trade Settlement Payment'),
        ('DCRD', 'Debit Card Payment'),
        ('DIVI', 'Dividend'),
        ('DVPM', 'Deliver Against Payment'),
        ('EPAY', 'ePayment'),
        ('FCOL', 'Fee Collection'),
        ('GOVT', 'Government Payment'),
        ('HEDG', 'Hedging'),
        ('ICCP', 'Irrevocable Credit Card Payment'),
        ('IDCP', 'Irrevocable Debit Card Payment'),
        ('INTC', 'Intra-Company Payment'),
        ('INTE', 'Interest'),
        ('LOAN', 'Loan'),
        ('OTHR', 'Other Payment'),
        ('PENS', 'Pension Payment'),
        ('RVPM', 'Receive Against Payment'),
        ('SALA', 'Salary Payment'),
        ('SECU', 'Securities'),
        ('SSBE', 'Social Security Benefit'),
        ('SUPP', 'Supplier Payment'),
        ('TAXS', 'Tax Payment'),
        ('TRAD', 'Trade'),
        ('TREA', 'Treasury Payment'),
        ('VATX', 'VAT Payment'),
        ('WHLD', 'WithHolding'),
        ], string="Category Purpose",
        help="If neither your bank nor your local regulations oblige you to "
        "set the category purpose, leave the field empty.")
    # PAIN allows 140 characters
    communication = fields.Char(size=140)
    # The field struct_communication_type has been dropped in v9
    # We now use communication_type ; you should add an option
    # in communication_type with selection_add=[]
    communication_type = fields.Selection(selection_add=[('ISO', 'ISO')])
