# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.misc import format_date, formatLang

from .account_payment_line import ACTIVE_ORDER_STATES

CASHFLOW_DAYS = 30
# Schedule states counted as money that still has to leave, by column of the chart.
OUTFLOW_STATES = {
    "queue": ("to_schedule", "missing_instrument", "blocked"),
    "draft": ("draft_order",),
    "bank": ("in_progress",),
}

SCHEDULE_STATES = [
    ("to_schedule", "To Schedule"),
    ("missing_instrument", "Missing Instrument"),
    ("blocked", "Blocked"),
    ("draft_order", "In Draft Order"),
    ("in_progress", "In Progress"),
    ("done", "Done"),
]


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    payment_schedule_date = fields.Date(
        string="Scheduled Payment Date",
        compute="_compute_payment_schedule_date",
        store=True,
        readonly=False,
        copy=False,
        help="Date on which this item should be paid. It starts as the due date.",
    )
    payment_schedule_state = fields.Selection(
        selection=SCHEDULE_STATES,
        string="Schedule Status",
        compute="_compute_payment_schedule_state",
        search="_search_payment_schedule_state",
    )
    payment_schedule_order_id = fields.Many2one(
        comodel_name="account.payment.order",
        string="Scheduled Payment Order",
        compute="_compute_payment_schedule_state",
    )

    payment_schedule_short_balance = fields.Boolean(
        string="Short of Cash",
        compute="_compute_payment_schedule_short_balance",
        search="_search_payment_schedule_short_balance",
        help="Scheduled on a date whose projected balance is below the minimum "
        "balance of the company.",
    )

    @api.depends("date_maturity", "account_id.account_type")
    def _compute_payment_schedule_date(self):
        for line in self:
            if line.account_type in ("asset_receivable", "liability_payable"):
                line.payment_schedule_date = line.date_maturity
            else:
                line.payment_schedule_date = False

    def _get_payment_schedule_lines(self):
        """Payment lines that still hold this item, so it cannot be scheduled again."""
        self.ensure_one()
        return self.payment_line_ids._filter_payment_schedule_holding()

    def _is_payment_schedule_instrument_missing(self):
        """The payment mode and, when its method needs one, the partner bank account."""
        self.ensure_one()
        mode = self.payment_mode_id
        if not mode.payment_order_ok:
            return True
        return mode.payment_method_id.bank_account_required and not (
            self.partner_bank_id or self.partner_id.bank_ids
        )

    @api.depends(
        "reconciled",
        "blocked",
        "payment_mode_id",
        "partner_bank_id",
        "payment_line_ids.state",
    )
    def _compute_payment_schedule_state(self):
        for line in self:
            paylines = line._get_payment_schedule_lines()
            drafts = paylines.filtered(lambda pl: pl.state == "draft")
            line.payment_schedule_order_id = (drafts or paylines)[:1].order_id
            if line.reconciled:
                line.payment_schedule_state = "done"
            elif paylines:
                line.payment_schedule_state = "draft_order" if drafts else "in_progress"
            elif line.blocked:
                line.payment_schedule_state = "blocked"
            elif line._is_payment_schedule_instrument_missing():
                line.payment_schedule_state = "missing_instrument"
            else:
                line.payment_schedule_state = "to_schedule"

    @api.model
    def _get_payment_schedule_missing_instrument_domain(self):
        """Search counterpart of ``_is_payment_schedule_instrument_missing``:
        modules that extend one extend the other."""
        return expression.OR(
            [
                [("payment_mode_id", "=", False)],
                [("payment_mode_id.payment_order_ok", "=", False)],
                [
                    (
                        "payment_mode_id.payment_method_id.bank_account_required",
                        "=",
                        True,
                    ),
                    ("partner_bank_id", "=", False),
                    ("partner_id.bank_ids", "=", False),
                ],
            ]
        )

    def _get_payment_schedule_state_domains(self):
        paylines = (
            self.env["account.payment.line"]
            .search(
                [("state", "in", ACTIVE_ORDER_STATES), ("move_line_id", "!=", False)]
            )
            ._filter_payment_schedule_holding()
        )
        in_draft = paylines.filtered(lambda pl: pl.state == "draft").move_line_id
        held = paylines.move_line_id
        free = [("reconciled", "=", False), ("id", "not in", held.ids)]
        missing = self._get_payment_schedule_missing_instrument_domain()
        return {
            "done": [("reconciled", "=", True)],
            "draft_order": [("reconciled", "=", False), ("id", "in", in_draft.ids)],
            "in_progress": [
                ("reconciled", "=", False),
                ("id", "in", (held - in_draft).ids),
            ],
            "blocked": free + [("blocked", "=", True)],
            "missing_instrument": free + [("blocked", "=", False)] + missing,
            "to_schedule": free
            + [("blocked", "=", False)]
            + expression.distribute_not(["!"] + missing),
        }

    def _search_payment_schedule_state(self, operator, value):
        if operator not in ("=", "!=", "in", "not in"):
            raise UserError(_("Unsupported search on the schedule status."))
        values = {value} if isinstance(value, str) else set(value or [])
        if operator in ("!=", "not in"):
            values = {state for state, _label in SCHEDULE_STATES} - values
        domains = self._get_payment_schedule_state_domains()
        return expression.OR([domains[state] for state in values if state in domains])

    def write(self, vals):
        if "payment_schedule_date" not in vals:
            return super().write(vals)
        if any(line.payment_schedule_state == "in_progress" for line in self):
            raise UserError(
                _(
                    "The payment date cannot change once the payment order is "
                    "confirmed. Cancel the order first."
                )
            )
        moving = self.filtered(
            lambda line: line.payment_schedule_state == "draft_order"
        )
        res = super().write(vals)
        if moving:
            # The draft order holds a single date: move the items to the order of
            # the new date.
            moving.payment_line_ids.filtered(lambda pl: pl.state == "draft").unlink()
            moving._payment_schedule_create_orders()
        return res

    def _prepare_payment_schedule_order_vals(self, payment_mode, date):
        vals = {
            "payment_mode_id": payment_mode.id,
            "date_prefered": "fixed",
            "date_scheduled": date,
            "description": _("Payment schedule of %s") % format_date(self.env, date),
        }
        if (
            payment_mode.bank_account_link == "variable"
            and len(payment_mode.variable_journal_ids) == 1
        ):
            vals["journal_id"] = payment_mode.variable_journal_ids.id
        return vals

    def _payment_schedule_create_orders(self):
        """Put the items in draft payment orders, one per payment mode and date.

        The core sets the date of every payment line from its order on confirmation,
        so each scheduled date gets its own order with a fixed date. A date in the
        past becomes today, as the core does not pay in the past, and is written
        back on the item.
        """
        today = fields.Date.context_today(self)
        order_model = self.env["account.payment.order"]
        groups = defaultdict(lambda: self.browse())
        for line in self:
            date = max(line.payment_schedule_date or today, today)
            groups[(line.payment_mode_id, date)] |= line
        orders = order_model.browse()
        for (payment_mode, date), lines in groups.items():
            order = order_model.search(
                [
                    ("payment_mode_id", "=", payment_mode.id),
                    ("state", "=", "draft"),
                    ("date_prefered", "=", "fixed"),
                    ("date_scheduled", "=", date),
                ],
                limit=1,
            )
            if not order:
                order = order_model.create(
                    lines._prepare_payment_schedule_order_vals(payment_mode, date)
                )
            lines.filtered(lambda line: line.payment_schedule_date != date).write(
                {"payment_schedule_date": date}
            )
            lines.create_payment_line_from_move_line(order)
            orders |= order
        return orders

    @api.model
    def _get_payment_schedule_dashboard_counters(self):
        """Counters shown on top of the schedule.

        Each counter opens the filter of the search view with the same name. Other
        modules add their own counters here.
        """
        today = fields.Date.context_today(self)
        return [
            {
                "filter": "to_schedule",
                "label": _("To Schedule"),
                "domain": [("payment_schedule_state", "=", "to_schedule")],
            },
            {
                "filter": "due_today",
                "label": _("Until Today"),
                "domain": [
                    ("reconciled", "=", False),
                    ("payment_schedule_date", "<=", today),
                ],
            },
            {
                "filter": "overdue",
                "label": _("Overdue"),
                "domain": [("reconciled", "=", False), ("date_maturity", "<", today)],
                "alert": True,
            },
            {
                "filter": "missing_instrument",
                "label": _("Missing Instrument"),
                "domain": [("payment_schedule_state", "=", "missing_instrument")],
                "alert": True,
            },
            {
                "filter": "draft_order",
                "label": _("In Draft Order"),
                "domain": [("payment_schedule_state", "=", "draft_order")],
            },
            {
                "filter": "in_progress",
                "label": _("In Progress"),
                "domain": [("payment_schedule_state", "=", "in_progress")],
            },
            {
                "filter": "short_balance",
                "label": _("Short of Cash"),
                "domain": [("payment_schedule_short_balance", "=", True)],
                "alert": True,
            },
        ]

    @api.model
    def retrieve_payment_schedule_dashboard(self, domain=None):
        """Count and amount of each counter, within the domain of the action."""
        self.check_access_rights("read")
        counters = []
        for counter in self._get_payment_schedule_dashboard_counters():
            groups = self.read_group(
                expression.AND([domain or [], counter["domain"]]),
                ["amount_residual:sum"],
                [],
            )
            row = groups[0] if groups else {}
            counters.append(
                {
                    "filter": counter["filter"],
                    "label": counter["label"],
                    "alert": counter.get("alert", False),
                    "count": row.get("__count", 0),
                    "amount": abs(row.get("amount_residual") or 0.0),
                }
            )
        return {"counters": counters, "currency_id": self.env.company.currency_id.id}

    def action_payment_schedule_create_orders(self):
        return {
            "name": _("Create Payment Orders"),
            "type": "ir.actions.act_window",
            "res_model": "account.payment.schedule.order",
            "view_mode": "form",
            "target": "new",
            "context": {"default_line_ids": [(6, 0, self.ids)]},
        }

    def action_payment_schedule_remove(self):
        """Take the items out of their draft payment orders, back to the schedule."""
        self.payment_line_ids.filtered(lambda pl: pl.state == "draft").unlink()

    @api.model
    def _get_payment_schedule_journals(self):
        return self.env["account.journal"].search(
            [("type", "in", ("bank", "cash")), ("company_id", "=", self.env.company.id)]
        )

    @api.model
    def _get_payment_schedule_opening_balance(self, journals):
        """Balance of the journals today: their bank or cash account, plus the
        payments already posted from them but not yet on a bank statement.

        Modules that read the balance from the bank override this.
        """
        method_lines = (
            journals.inbound_payment_method_line_ids
            | journals.outbound_payment_method_line_ids
        )
        outstanding = method_lines.payment_account_id
        outstanding |= journals.company_id.account_journal_payment_debit_account_id
        outstanding |= journals.company_id.account_journal_payment_credit_account_id
        domain = [
            ("parent_state", "=", "posted"),
            "|",
            ("account_id", "in", journals.default_account_id.ids),
            "&",
            ("account_id", "in", outstanding.ids),
            ("journal_id", "in", journals.ids),
        ]
        groups = self.read_group(domain, ["balance:sum"], [])
        return (groups[0]["balance"] or 0.0) if groups else 0.0

    @api.model
    def _get_payment_schedule_flow_domain(self, journals, all_journals):
        domain = [
            ("company_id", "=", self.env.company.id),
            ("parent_state", "=", "posted"),
            ("reconciled", "=", False),
        ]
        if not all_journals:
            domain += [
                "|",
                ("payment_mode_id.fixed_journal_id", "in", journals.ids),
                ("payment_mode_id.variable_journal_ids", "in", journals.ids),
            ]
        return domain

    @api.model
    def _get_payment_schedule_cashflow(self, journals=None, days=CASHFLOW_DAYS):
        """Projected balance per day, from today on.

        Inflows are the open receivables by due date (overdue ones are left out
        and returned apart); outflows are the open payables by scheduled date, a
        date in the past counting as today, as the payment orders do.
        """
        all_journals = journals is None
        journals = self._get_payment_schedule_journals() if all_journals else journals
        today = fields.Date.context_today(self)
        end = today + timedelta(days=days - 1)
        base = self._get_payment_schedule_flow_domain(journals, all_journals)
        flows = defaultdict(
            lambda: dict.fromkeys(("inflow", "queue", "draft", "bank"), 0.0)
        )
        receivables = base + [
            ("account_type", "=", "asset_receivable"),
            ("amount_residual", ">", 0),
        ]
        for line in self.search_read(
            receivables
            + [("date_maturity", ">=", today), ("date_maturity", "<=", end)],
            ["date_maturity", "amount_residual"],
        ):
            flows[line["date_maturity"]]["inflow"] += line["amount_residual"]
        overdue = self.read_group(
            receivables + [("date_maturity", "<", today)], ["amount_residual:sum"], []
        )
        payables = base + [
            ("account_type", "=", "liability_payable"),
            ("amount_residual", "<", 0),
            ("payment_schedule_date", "<=", end),
        ]
        for column, states in OUTFLOW_STATES.items():
            for line in self.search_read(
                payables + [("payment_schedule_state", "in", states)],
                ["payment_schedule_date", "amount_residual"],
            ):
                date = max(line["payment_schedule_date"] or today, today)
                flows[date][column] -= line["amount_residual"]
        balance = self._get_payment_schedule_opening_balance(journals)
        opening = balance
        series = []
        for offset in range(days):
            date = today + timedelta(days=offset)
            flow = flows[date]
            outflow = flow["queue"] + flow["draft"] + flow["bank"]
            balance += flow["inflow"] - outflow
            series.append(dict(flow, date=date, outflow=outflow, balance=balance))
        return {
            "opening": opening,
            "minimum": self.env.company.payment_schedule_minimum_balance,
            "overdue_receivable": (overdue[0]["amount_residual"] or 0.0)
            if overdue
            else 0.0,
            "days": series,
        }

    @api.model
    def _get_payment_schedule_short_dates(self, cashflow):
        return [
            day["date"]
            for day in cashflow["days"]
            if day["balance"] < cashflow["minimum"]
        ]

    @api.model
    def retrieve_payment_schedule_cashflow(self, journal_id=False):
        """Data of the cash flow chart on top of the payment schedule."""
        self.check_access_rights("read")
        journals = self._get_payment_schedule_journals()
        selected = journals.filtered(lambda journal: journal.id == journal_id)
        cashflow = self._get_payment_schedule_cashflow(selected or None)
        for day in cashflow["days"]:
            day["date"] = fields.Date.to_string(day["date"])
        cashflow.update(
            journals=[
                {"id": journal.id, "name": journal.display_name} for journal in journals
            ],
            journal_id=selected.id or False,
            currency_id=self.env.company.currency_id.id,
            short_days=len(self._get_payment_schedule_short_dates(cashflow)),
        )
        return cashflow

    def _payment_schedule_short_balance_domain(self):
        cashflow = self._get_payment_schedule_cashflow()
        dates = self._get_payment_schedule_short_dates(cashflow)
        if not dates:
            return expression.FALSE_DOMAIN
        today = fields.Date.context_today(self)
        date_domain = [("payment_schedule_date", "in", dates)]
        if today in dates:
            date_domain = expression.OR(
                [date_domain, [("payment_schedule_date", "<", today)]]
            )
        return expression.AND(
            [
                self._get_payment_schedule_flow_domain(None, True),
                [
                    ("account_type", "=", "liability_payable"),
                    ("amount_residual", "<", 0),
                ],
                date_domain,
            ]
        )

    def _compute_payment_schedule_short_balance(self):
        domain = self._payment_schedule_short_balance_domain()
        short = (
            self.browse()
            if domain == expression.FALSE_DOMAIN
            else self.filtered_domain(domain)
        )
        for line in self:
            line.payment_schedule_short_balance = line in short

    def _search_payment_schedule_short_balance(self, operator, value):
        if operator not in ("=", "!=") or not isinstance(value, bool):
            raise UserError(_("Unsupported search on the cash shortage."))
        domain = self._payment_schedule_short_balance_domain()
        if (operator == "=") == value:
            return domain
        return ["!"] + expression.normalize_domain(domain)

    @api.model
    def _get_payment_schedule_cash_warning(self, dates, journals=None):
        """Warning text for the given payment dates whose projected balance is
        below the minimum balance, with the first date from which it stays above."""
        cashflow = self._get_payment_schedule_cashflow(journals)
        currency = self.env.company.currency_id
        by_date = {day["date"]: day["balance"] for day in cashflow["days"]}
        today = fields.Date.context_today(self)
        all_short = self._get_payment_schedule_short_dates(cashflow)
        short = sorted({max(date, today) for date in dates if date} & set(all_short))
        if not short:
            return False
        messages = [
            _(
                "On %(date)s the projected balance is %(balance)s, below the "
                "minimum balance of %(minimum)s.",
                date=format_date(self.env, date),
                balance=formatLang(self.env, by_date[date], currency_obj=currency),
                minimum=formatLang(
                    self.env, cashflow["minimum"], currency_obj=currency
                ),
            )
            for date in short
        ]
        later = [day for day in cashflow["days"] if day["date"] > all_short[-1]]
        if later:
            messages.append(
                _(
                    "From %(date)s on, the projected balance stays above the minimum.",
                    date=format_date(self.env, later[0]["date"]),
                )
            )
        return "\n".join(messages)
