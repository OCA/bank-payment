# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo import api, fields, models
from odoo.osv import expression

from ..models.res_company import MAX_WORKDAY_SHIFT


class AccountPaymentLineCreate(models.TransientModel):
    _inherit = "account.payment.line.create"

    include_early_discount = fields.Boolean(
        string="Include Early Discounts",
        help="Also select invoices whose early payment discount must be paid in "
        "this period, even if their due date is later. For orders paying on the due "
        "date, only with the option 'Pay Early Discounts on Discount Date' of the "
        "payment mode (otherwise they are paid on the due date, without discount).",
    )

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        order = self.env["account.payment.order"].browse(res.get("order_id"))
        res["include_early_discount"] = (
            order.payment_mode_id.early_discount_pay_on_discount_date
        )
        return res

    def _early_discount_date_matches(self, date):
        if self.due_on == "between":
            return self.filter_date <= date <= (self.filter_date_end or date)
        if self.due_on == "=":
            return date == self.filter_date
        return date <= self.filter_date

    @api.depends("include_early_discount")
    def _compute_move_line_domain(self):
        res = super()._compute_move_line_domain()
        mode = self.order_id.payment_mode_id
        if not (
            self.include_early_discount
            and self.date_type == "due"
            and self.filter_date
            and mode
            and (
                mode.early_discount_pay_on_discount_date
                or self.order_id.date_prefered != "due"
            )
        ):
            return res
        # Same filters without the date filter (all fields, also those added by
        # other modules), then the early discount date
        values = {
            name: self[name]
            for name, field in self._fields.items()
            if field.store and not field.automatic
        }
        base = self.new(dict(values, date_type=False))
        super(AccountPaymentLineCreate, base)._compute_move_line_domain()
        today = fields.Date.context_today(self)
        # Older discount dates are past their deadline (grace days, then at most
        # MAX_WORKDAY_SHIFT days to the next working day); later ones are paid
        # after the filter date (buffer days, then at most MAX_WORKDAY_SHIFT days
        # back to the previous working day)
        oldest = today - timedelta(
            days=mode.early_discount_grace_days + MAX_WORKDAY_SHIFT
        )
        last = (
            self.filter_date_end
            if self.due_on == "between" and self.filter_date_end
            else self.filter_date
        )
        latest = last + timedelta(
            days=mode.early_discount_buffer_days + MAX_WORKDAY_SHIFT
        )
        candidates = self.env["account.move.line"].search(
            expression.AND(
                [
                    base.move_line_domain,
                    [
                        ("display_type", "=", "payment_term"),
                        ("discount_date", ">=", oldest),
                        ("discount_date", "<=", latest),
                    ],
                ]
            )
        )
        ids = []
        for aml in candidates:
            date = aml._get_payment_order_maturity_date(mode, early_discount=True)
            if date != aml.date_maturity and self._early_discount_date_matches(date):
                ids.append(aml.id)
        if ids:
            self.move_line_domain = expression.OR(
                [
                    self.move_line_domain,
                    expression.AND([base.move_line_domain, [("id", "in", ids)]]),
                ]
            )
        return res
