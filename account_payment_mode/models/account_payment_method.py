# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    code = fields.Char(
        string='Code (Do Not Modify)',
        help="This code is used in the code of the Odoo module that handles "
        "this payment method. Therefore, if you change it, "
        "the generation of the payment file may fail.")
    active = fields.Boolean(string='Active', default=True)
    bank_account_required = fields.Boolean(
        string='Bank Account Required',
        help="Activate this option if this payment method requires you to "
        "know the bank account number of your customer or supplier.")
    payment_mode_ids = fields.One2many(
        comodel_name='account.payment.mode', inverse_name='payment_method_id',
        string='Payment modes')

    @api.multi
    @api.depends('code', 'name', 'payment_type')
    def name_get(self):
        result = []
        for method in self:
            result.append((
                method.id,  u'[%s] %s (%s)' % (
                    method.code, method.name, method.payment_type)
            ))
        return result

    _sql_constraints = [(
        'code_payment_type_unique',
        'unique(code, payment_type)',
        'A payment method of the same type already exists with this code'
        )]
