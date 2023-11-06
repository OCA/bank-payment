# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class AccountPaymentOrder(models.Model):
    _name = "account.payment.order"
    _inherit = ["account.payment.order", "tier.validation"]
    _state_from = ["open"]
    _state_to = ["generated"]

    _tier_validation_manual_config = False
