# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    early_discount_pay_on_discount_date = fields.Boolean(
        string="Pay Early Discounts on Discount Date",
        help="Invoices with an early payment discount are selected by their discount "
        "date in 'Create Transactions' and scheduled on the discount date when the "
        "payment order uses the due date as payment execution date.",
    )
    early_discount_extend_to_workday = fields.Boolean(
        string="Extend Discount Period to Next Working Day",
        help="If the discount period ends on a non-working day of the company "
        "calendar (weekend, public holiday), the discount is still taken when "
        "paying on the next working day.",
    )
    early_discount_grace_days = fields.Integer(
        help="Additional days after the end of the discount period on which the "
        "discount is still taken (relying on the supplier's goodwill).",
    )
    early_discount_buffer_days = fields.Integer(
        help="Invoices with an early discount are selected and scheduled this many "
        "days before the end of the discount period (on the working day before), so "
        "that the money reaches the supplier in time. The discount stays valid until "
        "the end of the discount period.",
    )

    @api.constrains("early_discount_grace_days", "early_discount_buffer_days")
    def _check_early_discount_days(self):
        for mode in self:
            if (
                mode.early_discount_grace_days < 0
                or mode.early_discount_buffer_days < 0
            ):
                raise ValidationError(
                    self.env._(
                        "Early discount grace and buffer days cannot be negative."
                    )
                )
