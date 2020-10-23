# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoice(models.AbstractModel):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'account.payment.condition.mixin']
