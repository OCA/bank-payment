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
        string="Reference Type",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default="none",
    )

    @api.depends("payment_mode_id", "line_ids", "line_ids.payment_mode_id")
    def _compute_payment_order_ok(self):
        for move in self:
            payment_mode = move.line_ids.filtered(lambda x: not x.reconciled).mapped(
                "payment_mode_id"
            )[:1]
            if not payment_mode:
                payment_mode = move.payment_mode_id
            move.payment_order_ok = payment_mode.payment_order_ok

    def _get_payment_order_communication(self):
        """
        Retrieve the communication string for the payment order
        """
        communication = self.payment_reference or self.ref or self.name or ""
        if self.is_invoice():
            if (self.reference_type or "none") != "none":
                communication = self.ref
            elif self.is_purchase_document():
                communication = self.ref or self.payment_reference
            else:
                communication = self.payment_reference or self.name
        # If we have credit note(s) - reversal_move_id is a one2many
        if self.reversal_move_id:
            references = []
            references.extend(
                [
                    move._get_payment_order_communication()
                    for move in self.reversal_move_id
                    if move.payment_reference or move.ref
                ]
            )
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
            applicable_lines = move.line_ids.filtered(
                lambda x: (
                    not x.reconciled
                    and x.payment_mode_id.payment_order_ok
                    and x.account_id.internal_type in ("receivable", "payable")
                    and not any(
                        p_state in ("draft", "open", "generated")
                        for p_state in x.payment_line_ids.mapped("state")
                    )
                )
            )
            if not applicable_lines:
                raise UserError(
                    _(
                        "No Payment Line created for invoice %s because "
                        "it already exists or because this invoice is "
                        "already paid."
                    )
                    % move.name
                )
            payment_modes = applicable_lines.mapped("payment_mode_id")
            if not payment_modes:
                raise UserError(_("No Payment Mode on invoice %s") % move.name)
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
                    lambda x: x.payment_mode_id == payment_mode
                ):
                    if line.blocked and not payment_mode.allow_blocked:
                        raise UserError(
                            _(
                                "The journal item '%(line)s' related to "
                                "journal entry '%(move)s' is marked as litigation, "
                                "and the payment mode '%(pay_mode)s' "
                                "doesn't allow litigation lines."
                            )
                            % {
                                "line": line.display_name,
                                "move": move.display_name,
                                "pay_mode": payment_mode.display_name,
                            }
                        )
                    line.create_payment_line_from_move_line(payorder)
                    count += 1
                if new_payorder:
                    move.message_post(
                        body=_(
                            "%d payment lines added to the new draft payment "
                            "order <a href=# data-oe-model=account.payment.order "
                            "data-oe-id=%d>%s</a> which has been automatically created."
                        )
                        % (count, payorder.id, payorder.display_name)
                    )
                else:
                    move.message_post(
                        body=_(
                            "%d payment lines added to the existing draft "
                            "payment order "
                            "<a href=# data-oe-model=account.payment.order "
                            "data-oe-id=%d>%s</a>."
                        )
                        % (count, payorder.id, payorder.display_name)
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
