# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2018 Eska Yazılım ve Danışmanlık A.Ş (www.eskayazilim.com.tr)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    code = fields.Char(
        string='Code (Do Not Modify)',
        help="This code is used in the code of the Odoo module that handles "
        "this payment method. Therefore, if you change it, "
        "the generation of the payment file may fail.",
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    _sql_constraints = [(
        'code_payment_type_unique',
        'unique(code, payment_type)',
        'A payment method of the same type already exists with this code'
        )]
