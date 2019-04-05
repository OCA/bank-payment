# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_order_id = fields.Many2one(
        'account.payment.order', string='Payment Order', copy=False,
        readonly=True)
