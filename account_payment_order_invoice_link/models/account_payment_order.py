# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def action_view_in_invoice(self):
        invoices = self._get_in_invoices()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_in_invoice_type"
        )
        if len(invoices) > 1:
            action["domain"] = [("id", "in", invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref("account.view_move_form").id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = invoices.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        # Reset context to avoid unwanted default filters from action (since we
        # already have the right domain)
        action["context"] = {
            "default_move_type": "in_invoice",
        }
        return action

    def action_view_out_invoice(self):
        invoices = self._get_out_invoices()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_out_invoice_type"
        )
        if len(invoices) > 1:
            action["domain"] = [("id", "in", invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref("account.view_move_form").id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = invoices.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        # Reset context to avoid unwanted default filters from action (since we
        # already have the right domain)
        action["context"] = {
            "default_move_type": "out_invoice",
        }
        return action

    def _get_in_invoices(self):
        self.ensure_one()
        return self.payment_line_ids.move_line_id.move_id.filtered(
            lambda move: move.move_type in ("in_invoice", "in_refund", "in_receipt")
        )

    def _get_out_invoices(self):
        self.ensure_one()
        return self.payment_line_ids.move_line_id.move_id.filtered(
            lambda move: move.move_type in ("out_invoice", "out_refund", "out_receipt")
        )

    @api.depends("payment_line_ids.move_line_id")
    def _compute_invoice_count(self):
        for order in self:
            order.in_invoice_count = len(order._get_in_invoices())
            order.out_invoice_count = len(order._get_out_invoices())

    in_invoice_count = fields.Integer(compute="_compute_invoice_count")
    out_invoice_count = fields.Integer(compute="_compute_invoice_count")
