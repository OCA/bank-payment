# Copyright 2014 Compassion CH - Cyril Sester <csester@compassion.ch>
# Copyright 2014 Tecnativa - Pedro M. Baeza
# Copyright 2015-16 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    mandate_id = fields.Many2one(
        comodel_name="account.banking.mandate",
        compute="_compute_mandate_id",
        store=True,
        readonly=False,
        precompute=True,
        string="Direct Debit Mandate",
        domain=[("state", "=", "valid")],
        check_company=True,
    )
    mandate_required = fields.Boolean(
        related="order_id.payment_method_id.mandate_required"
    )

    @api.depends("partner_id", "move_line_id", "partner_bank_id")
    def _compute_mandate_id(self):
        for line in self:
            mandate = False
            move = line.move_line_id.move_id
            payment_method = line.order_id.payment_mode_id.payment_method_id
            if payment_method.mandate_required:
                if move and move.mandate_id:
                    mandate = move.mandate_id
                elif line.partner_bank_id or line.partner_id:
                    domain = [
                        ("state", "=", "valid"),
                        ("company_id", "=", line.company_id.id),
                    ]
                    if line.partner_bank_id:
                        domain.append(("partner_bank_id", "=", line.partner_bank_id.id))
                    elif line.partner_id:
                        domain.append(("partner_id", "=", line.partner_id.id))
                    mandate = self.env["account.banking.mandate"].search(
                        domain, limit=1
                    )
            line.mandate_id = mandate and mandate.id or False
            if mandate:
                line.partner_bank_id = mandate.partner_bank_id.id

    @api.constrains("mandate_id", "partner_bank_id")
    def _check_mandate_bank_link(self):
        for pline in self:
            if (
                pline.mandate_id
                and pline.partner_bank_id
                and pline.mandate_id.partner_bank_id != pline.partner_bank_id
            ):
                raise ValidationError(
                    _(
                        "The payment line number {line_number} has "
                        "the bank account  '{line_bank_account}' which "
                        "is not attached to the mandate '{mandate_ref}' "
                        "(this mandate is attached to the bank account "
                        "'{mandate_bank_account}')."
                    ).format(
                        line_number=pline.name,
                        line_bank_account=pline.partner_bank_id.acc_number,
                        mandate_ref=pline.mandate_id.unique_mandate_reference,
                        mandate_bank_account=pline.mandate_id.partner_bank_id.acc_number,
                    )
                )

    def draft2open_payment_line_check(self):
        res = super().draft2open_payment_line_check()
        if self.mandate_required and not self.mandate_id:
            raise UserError(_("Missing Mandate on payment line %s") % self.name)
        return res

    @api.model
    def _get_payment_line_grouping_fields(self):
        res = super()._get_payment_line_grouping_fields()
        res.append("mandate_id")
        return res
