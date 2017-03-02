# -*- coding: utf-8 -*-
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class AccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    bank_invoice_report = fields.Boolean(
        string="Print Bank Account",
        default=True,
        help="Uncheck this option to hide bank account in invoice report",
    )
