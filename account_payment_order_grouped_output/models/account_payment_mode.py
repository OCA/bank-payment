# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    generate_move = fields.Boolean(
        string="Generate Grouped Accounting Entries On File Upload", default=True
    )
    post_move = fields.Boolean(default=True)
