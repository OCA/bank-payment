# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'
    _rec_name = 'display_name'

    code = fields.Char(
        string='Code (Do Not Modify)',
        help="This code is used in the code of the Odoo module that handle "
        "this payment method. Therefore, if you change it, "
        "the generation of the payment file may fail.")
    active = fields.Boolean(string='Active', default=True)
    bank_account_required = fields.Boolean(
        string='Bank Account Required',
        help="Activate this option if this payment method requires you to "
        "know the bank account number of your customer or supplier.")
    display_name = fields.Char(
        compute='compute_display_name',
        store=True, string='Display Name')

    @api.multi
    @api.depends('code', 'name', 'payment_type')
    def compute_display_name(self):
        for method in self:
            method.display_name = u'[%s] %s (%s)' % (
                method.code, method.name, method.payment_type)

    _sql_constraints = [(
        'code_payment_type_unique',
        'unique(code, payment_type)',
        'A payment method of the same type already exists with this code'
        )]
