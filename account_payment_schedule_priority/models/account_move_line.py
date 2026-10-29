# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict
from datetime import timedelta

from odoo import Command, _, api, fields, models
from odoo.osv import expression
from odoo.tools.misc import format_date, formatLang

PAYMENT_PRIORITIES = [
    ("1", "Critical"),
    ("2", "High"),
    ("3", "Normal"),
    ("4", "Low"),
]
# An item of a confirmed payment order is at the bank already: it keeps its date.
REPLAN_STATES = ("to_schedule", "draft_order")


def _replan_order(line):
    """Lowest priority first and, within a priority, latest due date first."""
    due = line.date_maturity or line.payment_schedule_date
    return (-int(line.payment_priority or "3"), -due.toordinal(), -line.id)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    payment_priority = fields.Selection(
        selection=PAYMENT_PRIORITIES,
        compute="_compute_payment_priority",
        store=True,
        readonly=False,
    )

    @api.depends("partner_id")
    def _compute_payment_priority(self):
        for line in self:
            line.payment_priority = (
                line.partner_id.commercial_partner_id.payment_priority or "3"
            )

    @api.model
    def _get_payment_schedule_replan(self):
        """New dates for the lowest priority items of the dates short of cash.

        Each short date moves its items, in the order of ``_replan_order``, to the
        first later date from which the projected balance stays at or above the
        minimum, until it is no longer short. Moving an item raises only the
        balance of the days before its new date, so that date stays valid. With
        no such date in the horizon, the items are kept.
        """
        cashflow = self._get_payment_schedule_cashflow()
        minimum = cashflow["minimum"]
        dates = [day["date"] for day in cashflow["days"]]
        balance = {day["date"]: day["balance"] for day in cashflow["days"]}
        domain = expression.AND(
            [
                self._get_payment_schedule_flow_domain(None, True),
                [
                    ("account_type", "=", "liability_payable"),
                    ("amount_residual", "<", 0),
                    ("payment_schedule_date", "<=", dates[-1]),
                    ("payment_schedule_state", "in", REPLAN_STATES),
                    ("payment_priority", "!=", "1"),
                ],
            ]
        )
        items = defaultdict(lambda: self.browse())
        for line in self.search(domain):
            # A date in the past is paid today, as in the cash flow.
            items[max(line.payment_schedule_date, dates[0])] |= line
        moves = []
        kept = self.browse()
        for date in dates:
            for line in items[date].sorted(_replan_order):
                if balance[date] >= minimum:
                    break
                short = [day for day in dates if balance[day] < minimum]
                if short[-1] == dates[-1]:
                    kept |= line
                    continue
                new_date = dates[dates.index(short[-1]) + 1]
                for day in dates:
                    if date <= day < new_date:
                        balance[day] -= line.amount_residual
                moves.append((line, new_date))
        return {"moves": moves, "kept": kept, "minimum": minimum, "balance": balance}

    @api.model
    def _get_payment_schedule_replan_summary(self, plan):
        """The days that stay short of cash after the replan, in runs."""
        runs = []
        for date, balance in sorted(plan["balance"].items()):
            if balance >= plan["minimum"]:
                continue
            if runs and runs[-1][1] == date - timedelta(days=1):
                runs[-1] = (runs[-1][0], date, min(runs[-1][2], balance))
            else:
                runs.append((date, date, balance))
        currency = self.env.company.currency_id
        messages = []
        for start, end, lowest in runs:
            values = {
                "start": format_date(self.env, start),
                "end": format_date(self.env, end),
                "balance": formatLang(self.env, lowest, currency_obj=currency),
            }
            if start == end:
                messages.append(f"{values['start']}: {values['balance']}")
            else:
                messages.append(
                    _("%(start)s to %(end)s: down to %(balance)s", **values)
                )
        return "\n".join(messages) or False

    @api.model
    def action_payment_schedule_replan(self):
        plan = self._get_payment_schedule_replan()
        wizard = self.env["account.payment.schedule.replan"].create(
            {
                "short_summary": self._get_payment_schedule_replan_summary(plan),
                "move_ids": [
                    Command.create({"move_line_id": line.id, "new_date": date})
                    for line, date in plan["moves"]
                ],
                "kept_ids": [
                    Command.create({"move_line_id": line.id}) for line in plan["kept"]
                ],
            }
        )
        return {
            "name": _("Replan by Priority"),
            "type": "ir.actions.act_window",
            "res_model": wizard._name,
            "res_id": wizard.id,
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "new",
        }
