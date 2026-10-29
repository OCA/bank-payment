# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentScheduleOrder(models.TransientModel):
    _name = "account.payment.schedule.order"
    _description = "Create Payment Orders from the Payment Schedule"

    line_ids = fields.Many2many(comodel_name="account.move.line", string="Items")
    ready_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        compute="_compute_ready_line_ids",
        string="Items to Schedule",
    )
    skipped_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        compute="_compute_ready_line_ids",
        string="Items Left Out",
    )
    company_currency_id = fields.Many2one(
        comodel_name="res.currency", default=lambda self: self.env.company.currency_id
    )
    ready_amount = fields.Monetary(
        compute="_compute_ready_line_ids",
        currency_field="company_currency_id",
        string="Amount to Schedule",
    )
    cash_warning = fields.Text(compute="_compute_cash_warning")

    @api.depends("line_ids")
    def _compute_ready_line_ids(self):
        for wizard in self:
            ready = wizard.line_ids.filtered(
                lambda line: line.payment_schedule_state == "to_schedule"
            )
            wizard.ready_line_ids = ready
            wizard.skipped_line_ids = wizard.line_ids - ready
            wizard.ready_amount = abs(sum(ready.mapped("amount_residual")))

    @api.depends("ready_line_ids")
    def _compute_cash_warning(self):
        for wizard in self:
            wizard.cash_warning = self.env[
                "account.move.line"
            ]._get_payment_schedule_cash_warning(
                set(wizard.ready_line_ids.mapped("payment_schedule_date"))
            )

    def action_create_orders(self):
        self.ensure_one()
        if not self.ready_line_ids:
            raise UserError(_("None of the selected items can be scheduled."))
        orders = self.ready_line_ids._payment_schedule_create_orders()
        xmlid = (
            "account_payment_order.account_payment_order_inbound_action"
            if set(orders.mapped("payment_type")) == {"inbound"}
            else "account_payment_order.account_payment_order_outbound_action"
        )
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action["domain"] = [("id", "in", orders.ids)]
        return action
