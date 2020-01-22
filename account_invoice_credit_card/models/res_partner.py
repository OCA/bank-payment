# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    payment_token_id = fields.Many2one(
        comodel_name='payment.token',
        string='Default Payment Method')
