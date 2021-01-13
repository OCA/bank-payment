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
        string="Direct Debit Mandate",
        domain=[("state", "=", "valid")],
        check_company=True,
    )
    mandate_required = fields.Boolean(
        related="order_id.payment_method_id.mandate_required", readonly=True
    )

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
                        "The payment line number %s has the bank account "
                        "'%s' which is not attached to the mandate '%s' (this "
                        "mandate is attached to the bank account '%s')."
                    )
                    % (
                        pline.name,
                        pline.partner_bank_id.acc_number,
                        pline.mandate_id.unique_mandate_reference,
                        pline.mandate_id.partner_bank_id.acc_number,
                    )
                )

    @api.constrains("mandate_id", "company_id")
    def _check_company_constrains(self):
        for pline in self:
            if (
                pline.mandate_id.company_id
                and pline.mandate_id.company_id != pline.company_id
            ):
                raise ValidationError(
                    _(
                        "The payment line number %s a different company than "
                        "that of the linked mandate %s)."
                    )
                    % (pline.name, pline.mandate_id.display_name)
                )

    def draft2open_payment_line_check(self):
        res = super().draft2open_payment_line_check()
        if self.mandate_required and not self.mandate_id:
            raise UserError(_("Missing Mandate on payment line %s") % self.name)
        return res
