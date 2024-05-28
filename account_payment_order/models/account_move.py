# © 2013-2014 ACSONE SA (<https://acsone.eu>).
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_order_id = fields.Many2one(
        comodel_name="account.payment.order",
        string="Payment Order",
        copy=False,
        readonly=True,
        check_company=True,
    )
    payment_order_ok = fields.Boolean(compute="_compute_payment_order_ok")
    # we restore this field from <=v11 for now for preserving behavior
    # TODO: Check if we can remove it and base everything in something at
    # payment mode or company level
    reference_type = fields.Selection(
        selection=[("none", "Free Reference"), ("structured", "Structured Reference")],
        readonly=True,
        default="none",
    )
    payment_line_count = fields.Integer(compute="_compute_payment_line_count")

    @api.depends("payment_mode_id", "line_ids", "line_ids.payment_mode_id")
    def _compute_payment_order_ok(self):
        for move in self:
            payment_mode = move.line_ids.filtered(lambda x: not x.reconciled).mapped(
                "payment_mode_id"
            )[:1]
            if not payment_mode:
                payment_mode = move.payment_mode_id
            move.payment_order_ok = payment_mode.payment_order_ok

    def _compute_payment_line_count(self):
        for move in self:
            move.payment_line_count = len(
                self.env["account.payment.line"]._search(
                    [("move_line_id", "in", self.line_ids.ids)]
                )
            )

    def _get_payment_order_communication_direct(self):
        """Retrieve the communication string for this direct item."""
        communication = self.payment_reference or self.ref or self.name
        if self.is_invoice():
            if (self.reference_type or "none") != "none":
                communication = self.ref
            elif self.is_purchase_document():
                communication = self.ref or self.payment_reference
            else:
                communication = self.payment_reference or self.name
        return communication or ""

    def _get_payment_order_communication_full(self):
        """Retrieve the full communication string for the payment order.
        Reversal moves and partial payments references added.
        Avoid having everything in the same method to avoid infinite recursion
        with partial payments.
        """
        communication = self._get_payment_order_communication_direct()
        references = []
        # Build a recordset to gather moves from which references have already
        # taken in order to avoid duplicates
        reference_moves = self.env["account.move"].browse()
        # If we have credit note(s) - reversal_move_id is a one2many
        if self.reversal_move_id:
            references.extend(
                [
                    move._get_payment_order_communication_direct()
                    for move in self.reversal_move_id
                ]
            )
            reference_moves |= self.reversal_move_id
        # Retrieve partial payments - e.g.: manual credit notes
        (
            invoice_partials,
            exchange_diff_moves,
        ) = self._get_reconciled_invoices_partials()
        for (
            _x,
            _y,
            payment_move_line,
        ) in invoice_partials + exchange_diff_moves:
            payment_move = payment_move_line.move_id
            if payment_move not in reference_moves:
                references.append(
                    payment_move._get_payment_order_communication_direct()
                )
        # Add references to communication from lines move
        if references:
            communication += " " + " ".join(references)
        return communication

    def _prepare_new_payment_order(self, payment_mode=None):
        self.ensure_one()
        if payment_mode is None:
            payment_mode = self.env["account.payment.mode"]
        vals = {"payment_mode_id": payment_mode.id or self.payment_mode_id.id}
        # other important fields are set by the inherit of create
        # in account_payment_order.py
        return vals

    def get_account_payment_domain(self, payment_mode):
        return [("payment_mode_id", "=", payment_mode.id), ("state", "=", "draft")]

    def create_account_payment_line(self):
        apoo = self.env["account.payment.order"]
        result_payorder_ids = set()
        action_payment_type = "debit"
        for move in self:
            if move.state != "posted":
                raise UserError(_("The invoice %s is not in Posted state") % move.name)
            pre_applicable_lines = move.line_ids.filtered(
                lambda x: (
                    not x.reconciled
                    and x.account_id.account_type
                    in ("asset_receivable", "liability_payable")
                )
            )
            if not pre_applicable_lines:
                raise UserError(_("No pending AR/AP lines to add on %s") % move.name)
            payment_modes = pre_applicable_lines.mapped("payment_mode_id")
            if not payment_modes:
                raise UserError(_("No Payment Mode on invoice %s") % move.name)
            applicable_lines = pre_applicable_lines.filtered(
                lambda x: x.payment_mode_id.payment_order_ok
            )
            if not applicable_lines:
                raise UserError(
                    _(
                        "No Payment Line created for invoice %s because "
                        "its payment mode is not intended for payment orders."
                    )
                    % move.name
                )
            payment_lines = applicable_lines.payment_line_ids.filtered(
                lambda x: x.state in ("draft", "open", "generated")
            )
            if payment_lines:
                raise UserError(
                    _(
                        "The invoice %(move)s is already added in the payment "
                        "order(s) %(order)s."
                    )
                    % {
                        "move": move.name,
                        "order": payment_lines.order_id.mapped("name"),
                    }
                )
            for payment_mode in payment_modes:
                payorder = apoo.search(
                    move.get_account_payment_domain(payment_mode), limit=1
                )
                new_payorder = False
                if not payorder:
                    payorder = apoo.create(
                        move._prepare_new_payment_order(payment_mode)
                    )
                    new_payorder = True
                result_payorder_ids.add(payorder.id)
                action_payment_type = payorder.payment_type
                count = 0
                for line in applicable_lines.filtered(
                    lambda x, mode=payment_mode: x.payment_mode_id == mode
                ):
                    line.create_payment_line_from_move_line(payorder)
                    count += 1
                if new_payorder:
                    move.message_post(
                        body=_(
                            "%(count)d payment lines added to the new draft payment "
                            "order <a href=# data-oe-model=account.payment.order "
                            "data-oe-id=%(order_id)d>%(name)s</a>, which has been "
                            "automatically created.",
                            count=count,
                            order_id=payorder.id,
                            name=payorder.name,
                        )
                    )
                else:
                    move.message_post(
                        body=_(
                            "%(count)d payment lines added to the existing draft "
                            "payment order "
                            "<a href=# data-oe-model=account.payment.order "
                            "data-oe-id=%(order_id)d>%(name)s</a>.",
                            count=count,
                            order_id=payorder.id,
                            name=payorder.name,
                        )
                    )
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_payment_order.account_payment_order_%s_action"
            % action_payment_type,
        )
        if len(result_payorder_ids) == 1:
            action.update(
                {
                    "view_mode": "form,tree,pivot,graph",
                    "res_id": payorder.id,
                    "views": False,
                }
            )
        else:
            action.update(
                {
                    "view_mode": "tree,form,pivot,graph",
                    "domain": "[('id', 'in', %s)]" % list(result_payorder_ids),
                    "views": False,
                }
            )
        return action

    def action_payment_lines(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_payment_order.account_payment_line_action"
        )
        action.update(
            {
                "domain": [("move_line_id", "in", self.line_ids.ids)],
                "context": dict(
                    self.env.context,
                    account_payment_line_main_view=1,
                    form_view_ref="account_payment_order.account_payment_line_form_readonly",
                ),
            }
        )
        return action

    @api.model
    def _get_invoice_in_payment_state(self):
        """Called from _compute_payment_state method.
        Consider in_payment all the moves that are included in a payment order.
        """
        if self.line_ids.payment_line_ids:
            return "in_payment"
        return super()._get_invoice_in_payment_state()
