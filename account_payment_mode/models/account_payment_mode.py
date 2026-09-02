# Copyright 2016-2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentMode(models.Model):
    """This corresponds to the object payment.mode of v8 with some
    important changes. It also replaces the object payment.method
    of the module sale_payment_method of OCA/e-commerce"""

    _name = "account.payment.mode"
    _description = "Payment Modes"
    _order = "sequence, name"
    _check_company_auto = True

    name = fields.Char(required=True, translate=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        ondelete="restrict",
        default=lambda self: self.env.company,
    )
    bank_account_link = fields.Selection(
        [("fixed", "Fixed"), ("variable", "Variable")],
        string="Link to Bank Account",
        required=True,
        help="For payment modes that are always attached to the same bank "
        "account of your company (such as wire transfer from customers or "
        "SEPA direct debit from suppliers), select "
        "'Fixed'. For payment modes that are not always attached to the same "
        "bank account (such as SEPA Direct debit for customers, wire transfer "
        "to suppliers), you should select 'Variable', which means that you "
        "will select the bank account on the payment order. If your company "
        "only has one bank account, you should always select 'Fixed'.",
    )
    fixed_journal_id = fields.Many2one(
        "account.journal",
        string="Fixed Bank Journal",
        domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]",
        ondelete="restrict",
        check_company=True,
    )
    # I need to explicitly define the table name
    # because I have 2 M2M fields pointing to account.journal
    variable_journal_ids = fields.Many2many(
        comodel_name="account.journal",
        relation="account_payment_mode_variable_journal_rel",
        column1="payment_mode_id",
        column2="journal_id",
        string="Allowed Bank Journals",
        domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]",
    )
    payment_method_id = fields.Many2one(
        "account.payment.method",
        string="Payment Method",
        required=True,
        ondelete="restrict",
    )
    payment_type = fields.Selection(
        related="payment_method_id.payment_type", readonly=True, store=True
    )
    payment_method_code = fields.Char(
        related="payment_method_id.code", readonly=True, store=True
    )
    active = fields.Boolean(default=True)
    note = fields.Html(translate=True)
    sequence = fields.Integer(default=10)

    @api.onchange("company_id")
    def _onchange_company_id(self):
        self.variable_journal_ids = False
        self.fixed_journal_id = False

    @api.constrains("name", "company_id", "active")
    def _check_name_unique(self):
        """Forbid several active payment modes with the same name in a company.

        This is implemented as a Python constraint and not as a SQL UNIQUE
        constraint because 'name' is a translated field: it is stored as a
        jsonb column, so a unique index would compare the whole translation
        dictionary rather than the name the user actually sees. It would let
        {"en_US": "Boleto"} and {"en_US": "Boleto", "fr_FR": "Boleto"} coexist
        while wrongly rejecting two records that merely share the same
        translations.
        """
        modes = self.filtered("active")
        if not modes:
            return
        # sudo() because uniqueness must hold company-wide, even if multi-company
        # record rules hide part of the existing payment modes from the user.
        existing = (
            self.sudo()
            .with_context(active_test=True)
            .search([("company_id", "in", modes.company_id.ids)])
        )
        # Names are compared case-insensitively and without surrounding blanks:
        # "BOLETO", "Boleto" and "boleto " are duplicates for a human being.
        seen = {}
        for mode in existing - modes:
            seen.setdefault(mode._name_unique_key(), mode)
        for mode in modes:
            key = mode._name_unique_key()
            if key in seen:
                raise ValidationError(
                    _(
                        "There is already a payment mode named '%(existing)s' in "
                        "company %(company)s. Payment mode names must be unique "
                        "per company: please reuse that payment mode instead of "
                        "creating a new one, or choose a different name.",
                        existing=seen[key].name,
                        company=mode.company_id.display_name,
                    )
                )
            seen[key] = mode

    def _name_unique_key(self):
        """Key used to detect duplicated payment mode names."""
        self.ensure_one()
        return self._name_unique_key_for(self.company_id.id, self.name)

    @api.model
    def _name_unique_key_for(self, company_id, name):
        return (company_id, (name or "").strip().casefold())

    @api.model
    def _get_free_name(self, name, company_id, taken_keys):
        """Return `name` itself if free in that company, a "(copy)" one otherwise."""
        name = name or ""

        def is_free(candidate):
            return self._name_unique_key_for(company_id, candidate) not in taken_keys

        if is_free(name):
            return name
        candidate = _("%(name)s (copy)", name=name)
        counter = 2
        while not is_free(candidate):
            candidate = _("%(name)s (copy %(counter)s)", name=name, counter=counter)
            counter += 1
        return candidate

    def copy_data(self, default=None):
        """Rename copies whose name is already taken in the target company.

        Names are unique per active payment mode and company, so a copy cannot
        always keep the name of its original: fall back to a free "(copy)" name,
        the way Odoo core does for journals, instead of letting
        `_check_name_unique` reject the standard Duplicate action.
        """
        default = dict(default or {})
        vals_list = super().copy_data(default)
        if "name" in default:
            return vals_list
        company_ids = {
            vals.get("company_id") or mode.company_id.id
            for mode, vals in zip(self, vals_list, strict=False)
            if vals
        }
        # sudo() for the same reason as in `_check_name_unique`: the names to
        # avoid are the ones of the whole company, not only the visible ones.
        taken_keys = {
            mode._name_unique_key()
            for mode in self.sudo().search([("company_id", "in", list(company_ids))])
        }
        for mode, vals in zip(self, vals_list, strict=False):
            if not vals:
                continue
            company_id = vals.get("company_id") or mode.company_id.id
            vals["name"] = self._get_free_name(mode.name, company_id, taken_keys)
            taken_keys.add(self._name_unique_key_for(company_id, vals["name"]))
        return vals_list

    @api.constrains("bank_account_link", "fixed_journal_id", "payment_method_id")
    def bank_account_link_constrains(self):
        for mode in self.filtered(lambda x: x.bank_account_link == "fixed"):
            if not mode.fixed_journal_id:
                raise ValidationError(
                    _(
                        "On the payment mode %(name)s, the bank account link is "
                        "'Fixed' but the fixed bank journal is not set",
                        name=mode.name,
                    )
                )
            else:
                f_journal = mode.fixed_journal_id
                if mode.payment_method_id.payment_type == "outbound":
                    p_modes = f_journal.outbound_payment_method_line_ids.mapped(
                        "payment_method_id.id"
                    )
                    if mode.payment_method_id.id not in p_modes:
                        raise ValidationError(
                            _(
                                "On the payment mode %(paymode)s, the payment method "
                                "is %(paymethod)s, but this payment method is not part "
                                "of the payment methods of the fixed bank "
                                "journal %(journal)s",
                                paymode=mode.name,
                                paymethod=mode.payment_method_id.name,
                                journal=mode.fixed_journal_id.name,
                            )
                        )
                else:
                    p_modes = f_journal.inbound_payment_method_line_ids.mapped(
                        "payment_method_id.id"
                    )
                    if mode.payment_method_id.id not in p_modes:
                        raise ValidationError(
                            _(
                                "On the payment mode %(paymode)s, the payment method "
                                "is %(paymethod)s (it is in fact a debit method), "
                                "but this debit method is not part "
                                "of the debit methods of the fixed bank "
                                "journal %(journal)s",
                                paymode=mode.name,
                                paymethod=mode.payment_method_id.name,
                                journal=mode.fixed_journal_id.name,
                            )
                        )

    @api.constrains("company_id", "variable_journal_ids")
    def company_id_variable_journal_ids_constrains(self):
        for mode in self:
            if any(mode.company_id != j.company_id for j in mode.variable_journal_ids):
                raise ValidationError(
                    _(
                        "The company of the payment mode %(paymode)s, does not match "
                        "with one of the Allowed Bank Journals.",
                        paymode=mode.name,
                    )
                )
