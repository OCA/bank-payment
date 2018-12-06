# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    bank_account_required = fields.Boolean(
        string='Bank Account Required',
        help="Activate this option if this payment method requires you to "
        "know the bank account number of your customer or supplier.")

    payment_mode_ids = fields.One2many(
        comodel_name='account.payment.mode', inverse_name='payment_method_id',
        string='Payment modes')
