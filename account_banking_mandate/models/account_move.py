# Copyright 2020 Marçal Isern <marsal.isern@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    mandate_id = fields.Many2one(
        "account.banking.mandate",
        string="Direct Debit Mandate",
        ondelete="restrict",
        readonly=True,
        check_company=True,
        states={"draft": [("readonly", False)]},
    )
    mandate_required = fields.Boolean(
        related="payment_mode_id.payment_method_id.mandate_required", readonly=True
    )

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
                move = self.new(vals)
                move = move.with_company(move.company_id.id)
                getattr(move, onchange_method)()
                for field in changed_fields:
                    if field not in vals and move[field]:
                        vals[field] = move._fields[field].convert_to_write(
                            move[field], move
                        )
        return super().create(vals)

    def set_mandate(self):
        if self.payment_mode_id.payment_method_id.mandate_required:
            self.mandate_id = self.partner_id.valid_mandate_id
        else:
            self.mandate_id = False

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        """Select by default the first valid mandate of the partner"""
        res = super()._onchange_partner_id()
        self.set_mandate()
        return res

    @api.onchange("payment_mode_id")
    def _onchange_payment_mode_id(self):
        self.set_mandate()
