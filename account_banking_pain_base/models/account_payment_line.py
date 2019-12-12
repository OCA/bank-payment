# © 2013-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


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
    purpose = fields.Selection(
        # Full category purpose list found on:
        # https://www.iso20022.org/external_code_list.page
        # Document "External Code Sets spreadsheet" version 31 August, 2018
        selection=[
            ('ACCT', 'Account Management'),
            ('CASH', 'Cash Management Transfer'),
            ('COLL', 'Collection Payment'),
            ('INTC', 'Intra Company Payment'),
            ('LIMA', 'Liquidity Management'),
            ('NETT', 'Netting'),
            ('AGRT', 'Agricultural Transfer'),
            ('BEXP', 'Business Expenses'),
            ('COMC', 'Commercial Payment'),
            ('CPYR', 'Copyright'),
            ('GDDS', 'Purchase Sale Of Goods'),
            ('LICF', 'License Fee'),
            ('ROYA', 'Royalties'),
            ('SCVE', 'Purchase Sale Of Services'),
            ('SUBS', 'Subscription'),
            ('SUPP', 'Supplier Payment'),
            ('TRAD', 'Trade Services'),
            ('CHAR', 'Charity Payment'),
            ('COMT', 'Consumer Third Party Consolidated Payment'),
            ('CLPR', 'Car Loan Principal Repayment'),
            ('GOVI', 'Government Insurance'),
            ('HLRP', 'Housing Loan Repayment'),
            ('INSU', 'Insurance Premium'),
            ('INTE', 'Interest'),
            ('LBRI', 'Labor Insurance'),
            ('LIFI', 'Life Insurance'),
            ('LOAN', 'Loan'),
            ('LOAR', 'Loan Repayment'),
            ('PPTI', 'Property Insurance'),
            ('RINP', 'Recurring Installment Payment'),
            ('TRFD', 'Trust Fund'),
            ('ADVA', 'Advance Payment'),
            ('CCRD', 'Credit Card Payment '),
            ('CFEE', 'Cancellation Fee'),
            ('COST', 'Costs'),
            ('DCRD', 'Debit  Card  Payment'),
            ('GOVT', 'Government Payment'),
            ('IHRP', 'Instalment Hire Purchase Agreement'),
            ('INSM', 'Installment'),
            ('MSVC', 'Multiple Service Types'),
            ('NOWS', 'Not Otherwise Specified'),
            ('OFEE', 'Opening Fee'),
            ('OTHR', 'Other'),
            ('PADD', 'Preauthorized debit'),
            ('PTSP', 'Payment Terms'),
            ('RCPT', 'Receipt Payment'),
            ('RENT', 'Rent'),
            ('STDY', 'Study'),
            ('ANNI', 'Annuity'),
            ('CMDT', 'Commodity Transfer'),
            ('DERI', 'Derivatives'),
            ('DIVD', 'Dividend'),
            ('FREX', 'Foreign Exchange'),
            ('HEDG', 'Hedging'),
            ('PRME', 'Precious Metal'),
            ('SAVG', 'Savings'),
            ('SECU', 'Securities'),
            ('TREA', 'Treasury Payment'),
            ('ANTS', 'Anesthesia Services'),
            ('CVCF', 'Convalescent Care Facility'),
            ('DMEQ', 'Durable Medicale Equipment'),
            ('DNTS', 'Dental Services'),
            ('HLTC', 'Home Health Care'),
            ('HLTI', 'Health Insurance'),
            ('HSPC', 'Hospital Care'),
            ('ICRF', 'Intermediate Care Facility'),
            ('LTCF', 'Long Term Care Facility'),
            ('MDCS', 'Medical Services'),
            ('VIEW', 'Vision Care'),
            ('ALMY', 'Alimony Payment'),
            ('BECH', 'Child Benefit'),
            ('BENE', 'Unemployment Disability Benefit'),
            ('BONU', 'Bonus Payment.'),
            ('COMM', 'Commission'),
            ('PENS', 'Pension Payment'),
            ('PRCP', 'Price Payment'),
            ('SALA', 'Salary Payment'),
            ('SSBE', 'Social Security Benefit'),
            ('ESTX', 'Estate Tax'),
            ('HSTX', 'Housing Tax'),
            ('INTX', 'Income Tax'),
            ('TAXS', 'Tax Payment'),
            ('VATX', 'Value Added Tax Payment'),
            ('AIRB', 'Air'),
            ('BUSB', 'Bus'),
            ('FERB', 'Ferry'),
            ('RLWY', 'Railway'),
            ('CBTV', 'Cable TV Bill'),
            ('ELEC', 'Electricity Bill'),
            ('ENRG', 'Energies'),
            ('GASB', 'Gas Bill'),
            ('NWCH', 'Network Charge'),
            ('NWCM', 'Network Communication'),
            ('OTLC', 'Other Telecom Related Bill'),
            ('PHON', 'Telephone Bill'),
            ('WTER', 'Water Bill'),
        ],
        help="If neither your bank nor your local regulations oblige you to "
             "set the category purpose, leave the field empty.",
    )
    # PAIN allows 140 characters
    communication = fields.Char(size=140)
    # The field struct_communication_type has been dropped in v9
    # We now use communication_type ; you should add an option
    # in communication_type with selection_add=[]
    communication_type = fields.Selection(selection_add=[('ISO', 'ISO')])

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
             "and/or scheme (SEPA Core messages must use this). "
             "\nShared : transaction charges on the debtor side are to be "
             "borne by the debtor, transaction charges on the creditor side "
             "are to be borne by the creditor. \n Borne by creditor : all "
             "transaction charges are to be borne by the creditor. \nBorne "
             "by debtor : all transaction charges are to be borne by the "
             "debtor.")
    sepa = fields.Boolean(
        compute='compute_sepa', readonly=True, string="SEPA Payment Line")

    @api.multi
    @api.onchange('sepa')
    def compute_charge_bearer(self):
        for line in self:
            if line.sepa:
                line.charge_bearer = 'SLEV'
            else:
                if line.order_id.charge_bearer:
                    line.charge_bearer = line.order_id.charge_bearer

    @api.multi
    @api.depends(
        'order_id.company_partner_bank_id.acc_type',
        'currency_id',
        'partner_bank_id.acc_type')
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
