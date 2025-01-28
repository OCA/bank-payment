# © 2013-2014 ACSONE SA (<https://acsone.eu>).
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from markupsafe import Markup

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    # TODO what is this field for ????
    payment_order_id = fields.Many2one(
        comodel_name="account.payment.order",
        string="Payment Order",
        copy=False,
        readonly=True,
        check_company=True,
    )
    payment_order_ok = fields.Boolean(
        related="preferred_payment_method_line_id.payment_order_ok"
    )
    # we restore this field from <=v11 for now for preserving behavior
    # in v16, we have a field invoice_reference_type on sale journals
    # but it's not relevant because companies don't have a sale journal per country
    # and we need it for supplier invoices too
    reference_type = fields.Selection(
        selection=[("free", "Free Reference"), ("structured", "Structured Reference")],
        readonly=True,
        default="free",
    )
    payment_line_count = fields.Integer(compute="_compute_payment_line_count")

    # TODO convert to read group ?
    def _compute_payment_line_count(self):
        for move in self:
            move.payment_line_count = len(
                self.env["account.payment.line"]._search(
                    [("move_line_id", "in", self.line_ids.ids)]
                )
            )

    # Enable support for payment_state = "in_payment" on invoices
    # _get_invoice_in_payment_state() is a method of the "account" module
    # which returns "paid"
    @api.model
    def _get_invoice_in_payment_state(self):
        return "in_payment"

    def _get_payment_order_communication_direct(self):
        """Retrieve the communication string for this direct item."""
        communication = self.payment_reference or self.ref or self.name or ""
        return communication

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
        # If we have credit note(s)
        if self.reversal_move_ids:
            references.extend(
                [
                    move._get_payment_order_communication_direct()
                    for move in self.reversal_move_ids
                ]
            )
            reference_moves |= self.reversal_move_ids
        # Retrieve partial payments - e.g.: manual credit notes
        (
            invoice_partials,
            exchange_diff_moves,
        ) = self._get_reconciled_invoices_partials()
        for (
            _x,
            _y,
            payment_move_line,
        ) in invoice_partials:
            payment_move = payment_move_line.move_id
            if payment_move not in reference_moves:
                references.append(
                    payment_move._get_payment_order_communication_direct()
                )
        # Add references to communication from lines move
        if references:
            communication += " " + " ".join(references)
        return communication

    def _prepare_new_payment_order(self, payment_method_line=None):
        self.ensure_one()
        if not payment_method_line:
            payment_method_line = self.preferred_payment_method_line_id

        vals = {
            "payment_method_line_id": payment_method_line.id,
            "payment_type": payment_method_line.payment_type,
            "company_id": self.company_id.id,
        }
        # other important fields are set by the inherit of create
        # in account_payment_order.py
        return vals

    def get_account_payment_domain(self, payment_method_line):
        return [
            ("payment_method_line_id", "=", payment_method_line.id),
            ("state", "=", "draft"),
        ]

    def create_account_payment_line(self):
        apoo = self.env["account.payment.order"]
        result_payorder_ids = set()
        action_payment_type = "debit"
        for move in self:
            if move.state != "posted":
                raise UserError(
                    _("The invoice '%s' is not in Posted state.") % move.display_name
                )
            applicable_lines = move.line_ids.filtered(
                lambda x: (
                    not x.reconciled
                    and x.account_id.account_type
                    in ("asset_receivable", "liability_payable")
                )
            )
            if not applicable_lines:
                raise UserError(
                    _("No pending AR/AP lines to add on invoice '%s'.")
                    % move.display_name
                )
            payment_mode = move.preferred_payment_method_line_id
            if not payment_mode:
                raise UserError(
                    _("No Payment Mode on invoice '%s'.") % move.display_name
                )
            if not payment_mode.payment_order_ok:
                raise UserError(
                    _(
                        "No Payment Line created for invoice '%(invoice)s' because "
                        "its payment mode '%(pay_mode)s' is not intended for payment "
                        "orders.",
                        invoice=move.display_name,
                        pay_mode=payment_mode.display_name,
                    )
                )
            payment_lines = applicable_lines.payment_line_ids.filtered(
                lambda line: line.state in ("draft", "open", "generated")
            )
            if payment_lines:
                raise UserError(
                    _(
                        "The invoice %(move)s is already added in the payment "
                        "order(s) %(order)s.",
                        move=move.display_name,
                        order=", ".join(
                            [order.name for order in payment_lines.order_id]
                        ),
                    )
                )
            payorder = apoo.search(
                move.get_account_payment_domain(payment_mode), limit=1
            )
            new_payorder = False
            if not payorder:
                payorder = apoo.create(move._prepare_new_payment_order(payment_mode))
                new_payorder = True
            result_payorder_ids.add(payorder.id)
            action_payment_type = payorder.payment_type
            count = 0
            for line in applicable_lines:
                line.create_payment_line_from_move_line(payorder)
                count += 1
            pay_order_link = Markup(
                f"<a href=# data-oe-model=account.payment.order "
                f"data-oe-id={payorder.id}>{payorder.name}</a>"
            )
            if new_payorder:
                move.message_post(
                    body=_(
                        "%(count)d payment lines added to the new draft payment order "
                        "%(pay_order_link)s, which has been automatically created.",
                        count=count,
                        pay_order_link=pay_order_link,
                    )
                )
            else:
                move.message_post(
                    body=_(
                        "%(count)d payment lines added to the existing draft "
                        "payment order %(pay_order_link)s.",
                        count=count,
                        pay_order_link=pay_order_link,
                    )
                )
        action = self.env["ir.actions.act_window"]._for_xml_id(
            f"account_payment_order.account_payment_order_{action_payment_type}_action"
        )
        if len(result_payorder_ids) == 1:
            action.update(
                {
                    "view_mode": "form,list,pivot,graph",
                    "res_id": payorder.id,
                    "views": False,
                }
            )
        else:
            action.update(
                {
                    "view_mode": "list,form,pivot,graph",
                    "domain": f"[('id', 'in', {list(result_payorder_ids)})]",
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
