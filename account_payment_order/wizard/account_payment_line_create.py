# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<https://therp.nl>)
# © 2014-2015 ACSONE SA/NV (<https://acsone.eu>)
# © 2015-2016 Akretion (<https://www.akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountPaymentLineCreate(models.TransientModel):
    _name = "account.payment.line.create"
    _description = "Wizard to create payment lines"

    order_id = fields.Many2one(
        comodel_name="account.payment.order", string="Payment Order"
    )
    journal_ids = fields.Many2many(
        comodel_name="account.journal", string="Journals Filter"
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Partners",
        domain=[("parent_id", "=", False)],
    )
    target_move = fields.Selection(
        selection=[("posted", "All Posted Entries"), ("all", "All Entries")],
        string="Target Moves",
    )
    invoice = fields.Boolean(string="Linked to an Invoice or Refund")
    date_type = fields.Selection(
        selection=[("due", "Due Date"), ("move", "Move Date")],
        string="Type of Date Filter",
        required=True,
    )
    due_on = fields.Selection(
        string="Due on",
        selection=[("<=", "Before or equal"), ("=", "Equal"), ("between", "Between")],
        default="<=",
        required=True,
    )
    filter_date = fields.Date(default=fields.Date.context_today)
    filter_date_end = fields.Date(
        help="For 'Due on' 'Between', date between 'Filter Date' and 'Filter Date End'",
    )
    payment_mode = fields.Selection(
        selection=[("same", "Same"), ("same_or_null", "Same or Empty"), ("any", "Any")],
    )
    move_line_ids = fields.Many2many(
        comodel_name="account.move.line", string="Move Lines"
    )
    move_line_domain = fields.Binary(compute="_compute_move_line_domain")

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        context = self.env.context
        assert (
            context.get("active_model") == "account.payment.order"
        ), "active_model should be payment.order"
        assert context.get("active_id"), "Missing active_id in context !"
        order = self.env["account.payment.order"].browse(context["active_id"])
        mode = order.payment_mode_id
        res.update(
            {
                "journal_ids": [(6, 0, mode.default_journal_ids.ids)]
                if mode.default_journal_ids
                else False,
                "target_move": mode.default_target_move,
                "invoice": mode.default_invoice,
                "date_type": mode.default_date_type,
                "payment_mode": mode.default_payment_mode,
                "order_id": order.id,
            }
        )
        return res

    @api.depends(
        "date_type",
        "due_on",
        "filter_date",
        "filter_date_end",
        "journal_ids",
        "invoice",
        "target_move",
        "payment_mode",
        "partner_ids",
    )
    def _compute_move_line_domain(self):
        self.ensure_one()
        domain = [
            ("reconciled", "=", False),
            ("company_id", "=", self.order_id.company_id.id),
        ]
        if self.journal_ids:
            domain += [("journal_id", "in", self.journal_ids.ids)]
        if self.partner_ids:
            domain += [("partner_id", "in", self.partner_ids.ids)]
        if self.target_move == "posted":
            domain += [("move_id.state", "=", "posted")]
        else:
            domain += [("move_id.state", "in", ("draft", "posted"))]
        if self.date_type == "due":
            if self.due_on == "between":
                domain += [
                    "&",
                    ("date_maturity", ">=", self.filter_date),
                    ("date_maturity", "<=", self.filter_date_end),
                ]
            else:
                domain += [
                    "|",
                    ("date_maturity", self.due_on, self.filter_date),
                    ("date_maturity", "=", False),
                ]
        elif self.date_type == "move":
            if self.due_on == "between":
                domain += [
                    "&",
                    ("date", ">=", self.filter_date),
                    ("date", "<=", self.filter_date_end),
                ]
            else:
                domain.append(("date", self.due_on, self.filter_date))
        if self.invoice:
            domain.append(
                (
                    "move_id.move_type",
                    "in",
                    ("in_invoice", "out_invoice", "in_refund", "out_refund"),
                )
            )
        if self.payment_mode:
            if self.payment_mode == "same":
                domain.append(
                    ("payment_mode_id", "=", self.order_id.payment_mode_id.id)
                )
            elif self.payment_mode == "same_or_null":
                domain += [
                    "|",
                    ("payment_mode_id", "=", False),
                    ("payment_mode_id", "=", self.order_id.payment_mode_id.id),
                ]

        if self.order_id.payment_type == "outbound":
            # For payables, propose all unreconciled credit lines,
            # including partially reconciled ones.
            # If they are partially reconciled with a supplier refund,
            # the residual will be added to the payment order.
            #
            # For receivables, propose all unreconciled credit lines.
            # (ie customer refunds): they can be refunded with a payment.
            # Do not propose partially reconciled credit lines,
            # as they are deducted from a customer invoice, and
            # will not be refunded with a payment.
            domain += [
                ("credit", ">", 0),
                (
                    "account_id.account_type",
                    "in",
                    ["liability_payable", "asset_receivable"],
                ),
            ]
        elif self.order_id.payment_type == "inbound":
            domain += [
                ("debit", ">", 0),
                (
                    "account_id.account_type",
                    "in",
                    ["asset_receivable", "liability_payable"],
                ),
            ]
        # Exclude lines that are already in a non-cancelled
        # and non-uploaded payment order; lines that are in a
        # uploaded payment order are proposed if they are not reconciled,
        paylines = self.env["account.payment.line"].search(
            [
                ("state", "in", ("draft", "open", "generated")),
                ("move_line_id", "!=", False),
            ]
        )
        if paylines:
            move_lines_ids = [payline.move_line_id.id for payline in paylines]
            domain += [("id", "not in", move_lines_ids)]
        self.move_line_domain = domain

    def populate(self):
        lines = self.env["account.move.line"].search(self.move_line_domain)
        self.move_line_ids = lines
        action = {
            "name": self.env._("Select Move Lines to Create Transactions"),
            "type": "ir.actions.act_window",
            "res_model": "account.payment.line.create",
            "view_mode": "form",
            "target": "new",
            "res_id": self.id,
            "context": self._context,
        }
        return action

    def create_payment_lines(self):
        if self.move_line_ids:
            self.move_line_ids.create_payment_line_from_move_line(self.order_id)
        return True
