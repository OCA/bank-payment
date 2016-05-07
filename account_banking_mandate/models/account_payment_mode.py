# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    mandate_required = fields.Boolean(
        string='Mandate Required',
        help="Activate this option is this payment mode requires your "
        "customer to sign a direct debit mandate with your company.")
