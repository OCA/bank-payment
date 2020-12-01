# Copyright 2020 Marçal Isern <marsal.isern@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    mandate_id = fields.Many2one(
        "account.banking.mandate",
        string="Direct Debit Mandate",
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    mandate_required = fields.Boolean(
        related="payment_mode_id.payment_method_id.mandate_required", readonly=True
    )

    def post(self):
        for record in self:
            record.line_ids.write({"mandate_id": record.mandate_id})
        return super(AccountMove, self).post()

    @api.model
    def create(self, vals):
        """Fill the mandate_id from the partner if none is provided on
        creation, using same method as upstream."""
        onchanges = {
            "_onchange_partner_id": ["mandate_id"],
            "_onchange_payment_mode_id": ["mandate_id"],
        }
        for onchange_method, changed_fields in list(onchanges.items()):
            if any(f not in vals for f in changed_fields):
                invoice = self.new(vals)
                invoice = invoice.with_context(force_company=invoice.company_id.id,)
                getattr(invoice, onchange_method)()
                for field in changed_fields:
                    if field not in vals and invoice[field]:
                        vals[field] = invoice._fields[field].convert_to_write(
                            invoice[field], invoice
                        )
        return super(AccountMove, self).create(vals)

    def set_mandate(self):
        if self.payment_mode_id.payment_method_id.mandate_required:
            self.mandate_id = self.partner_id.valid_mandate_id
        else:
            self.mandate_id = False

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        """Select by default the first valid mandate of the partner"""
        res = super(AccountMove, self)._onchange_partner_id()
        self.set_mandate()
        return res

    @api.onchange("payment_mode_id")
    def _onchange_payment_mode_id(self):
        self.set_mandate()

    @api.constrains("mandate_id", "company_id")
    def _check_company_constrains(self):
        for inv in self:
            if (
                inv.mandate_id.company_id
                and inv.mandate_id.company_id != inv.company_id
            ):
                raise ValidationError(
                    _(
                        "The invoice %s has a different company than "
                        "that of the linked mandate %s)."
                    )
                    % (inv.name, inv.mandate_id.display_name)
                )
