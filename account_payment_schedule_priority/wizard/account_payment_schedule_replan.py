# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentScheduleReplan(models.TransientModel):
    _name = "account.payment.schedule.replan"
    _description = "Replan the Payment Schedule by Priority"

    move_ids = fields.One2many(
        comodel_name="account.payment.schedule.replan.line",
        inverse_name="wizard_id",
        domain=[("new_date", "!=", False)],
        string="Items to Move",
    )
    kept_ids = fields.One2many(
        comodel_name="account.payment.schedule.replan.line",
        inverse_name="wizard_id",
        domain=[("new_date", "=", False)],
        string="Items Kept",
    )
    short_summary = fields.Text(string="Still Short of Cash")

    def action_apply(self):
        self.ensure_one()
        for new_date in set(self.move_ids.mapped("new_date")):
            self.move_ids.filtered(
                lambda line, d=new_date: line.new_date == d
            ).move_line_id.write({"payment_schedule_date": new_date})
        return {"type": "ir.actions.act_window_close"}


class AccountPaymentScheduleReplanLine(models.TransientModel):
    _name = "account.payment.schedule.replan.line"
    _description = "Item of the Payment Schedule Replan"

    wizard_id = fields.Many2one(
        comodel_name="account.payment.schedule.replan",
        required=True,
        ondelete="cascade",
    )
    move_line_id = fields.Many2one(
        comodel_name="account.move.line", required=True, ondelete="cascade"
    )
    new_date = fields.Date()
    partner_id = fields.Many2one(related="move_line_id.partner_id")
    move_id = fields.Many2one(related="move_line_id.move_id")
    payment_priority = fields.Selection(related="move_line_id.payment_priority")
    date_maturity = fields.Date(related="move_line_id.date_maturity")
    payment_schedule_date = fields.Date(related="move_line_id.payment_schedule_date")
    amount_residual = fields.Monetary(
        related="move_line_id.amount_residual", currency_field="company_currency_id"
    )
    company_currency_id = fields.Many2one(related="move_line_id.company_currency_id")
