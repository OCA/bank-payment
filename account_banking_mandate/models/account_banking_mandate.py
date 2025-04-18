# Copyright 2014 Compassion CH - Cyril Sester <csester@compassion.ch>
# Copyright 2014 Tecnativa - Pedro M. Baeza
# Copyright 2015-2020 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountBankingMandate(models.Model):
    """The banking mandate is attached to a bank account and represents an
    authorization that the bank account owner gives to a company for a
    specific operation (such as direct debit)
    """

    _name = "account.banking.mandate"
    _description = "A generic banking mandate"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "signature_date desc"
    _check_company_auto = True

    def _get_default_partner_bank_id_domain(self):
        if "default_partner_id" in self.env.context:
            return [("partner_id", "=", self.env.context.get("default_partner_id"))]
        else:
            return []

    format = fields.Selection(
        [("basic", "Basic Mandate")],
        default="basic",
        required=True,
        string="Mandate Format",
        tracking=20,
    )
    type = fields.Selection(
        [("generic", "Generic Mandate")],
        string="Type of Mandate",
        tracking=30,
    )
    partner_bank_id = fields.Many2one(
        comodel_name="res.partner.bank",
        string="Bank Account",
        tracking=40,
        domain=lambda self: self._get_default_partner_bank_id_domain(),
        ondelete="restrict",
        index="btree",
        check_company=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="partner_bank_id.partner_id",
        string="Partner",
        store=True,
        index="btree",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    unique_mandate_reference = fields.Char(tracking=10, copy=False, default="/")
    signature_date = fields.Date(
        string="Date of Signature of the Mandate",
        tracking=50,
    )
    scan = fields.Binary(string="Scan of the Mandate")
    last_debit_date = fields.Date(string="Date of the Last Debit", readonly=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("valid", "Valid"),
            ("expired", "Expired"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=60,
        help="Only valid mandates can be used in a payment line. A cancelled "
        "mandate is a mandate that has been cancelled by the customer.",
    )
    payment_line_ids = fields.One2many(
        comodel_name="account.payment.line",
        inverse_name="mandate_id",
        string="Related Payment Lines",
    )
    payment_line_ids_count = fields.Integer(compute="_compute_payment_line_ids_count")

    _sql_constraints = [
        (
            "mandate_ref_company_uniq",
            "unique(unique_mandate_reference, company_id)",
            "A Mandate with the same reference already exists for this company!",
        )
    ]

    def name_get(self):
        result = []
        for mandate in self:
            name = mandate.unique_mandate_reference
            acc_number = mandate.partner_bank_id.acc_number
            if acc_number:
                name = "{} [...{}]".format(name, acc_number[-4:])
            result.append((mandate.id, name))
        return result

    @api.depends("payment_line_ids")
    def _compute_payment_line_ids_count(self):
        payment_line_model = self.env["account.payment.line"]
        domain = [("mandate_id", "in", self.ids)]
        res = payment_line_model.read_group(
            domain=domain, fields=["mandate_id"], groupby=["mandate_id"]
        )
        payment_line_dict = {}
        for dic in res:
            mandate_id = dic["mandate_id"][0]
            payment_line_dict.setdefault(mandate_id, 0)
            payment_line_dict[mandate_id] += dic["mandate_id_count"]
        for rec in self:
            rec.payment_line_ids_count = payment_line_dict.get(rec.id, 0)

    def show_payment_lines(self):
        self.ensure_one()
        return {
            "name": _("Payment lines"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "account.payment.line",
            "domain": [("mandate_id", "=", self.id)],
        }

    @api.constrains("signature_date", "last_debit_date")
    def _check_dates(self):
        today = fields.Date.context_today(self)
        for mandate in self:
            if mandate.signature_date and mandate.signature_date > today:
                raise ValidationError(
                    _("The date of signature of mandate '%s' " "is in the future!")
                    % mandate.unique_mandate_reference
                )
            if (
                mandate.signature_date
                and mandate.last_debit_date
                and mandate.signature_date > mandate.last_debit_date
            ):
                raise ValidationError(
                    _(
                        "The mandate '%s' can't have a date of last debit "
                        "before the date of signature."
                    )
                    % mandate.unique_mandate_reference
                )

    @api.constrains("state", "partner_bank_id", "signature_date")
    def _check_valid_state(self):
        for mandate in self:
            if mandate.state == "valid":
                if not mandate.signature_date:
                    raise ValidationError(
                        _(
                            "Cannot validate the mandate '%s' without a date of "
                            "signature."
                        )
                        % mandate.unique_mandate_reference
                    )
                if not mandate.partner_bank_id:
                    raise ValidationError(
                        _(
                            "Cannot validate the mandate '%s' because it is not "
                            "attached to a bank account."
                        )
                        % mandate.unique_mandate_reference
                    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if (vals.get("unique_mandate_reference") or "/") == "/":
                vals["unique_mandate_reference"] = (
                    self.env["ir.sequence"].next_by_code("account.banking.mandate")
                    or "New"
                )
        return super().create(vals_list)

    @api.onchange("partner_bank_id")
    def mandate_partner_bank_change(self):
        for mandate in self:
            mandate.partner_id = mandate.partner_bank_id.partner_id

    def validate(self):
        for mandate in self:
            if mandate.state != "draft":
                raise UserError(_("Mandate should be in draft state."))
        self.write({"state": "valid"})

    def cancel(self):
        for mandate in self:
            if mandate.state not in ("draft", "valid"):
                raise UserError(_("Mandate should be in draft or valid state."))
        self.write({"state": "cancel"})

    def back2draft(self):
        """Allows to set the mandate back to the draft state.
        This is for mandates cancelled by mistake.
        """
        for mandate in self:
            if mandate.state != "cancel":
                raise UserError(_("Mandate should be in cancel state."))
        self.write({"state": "draft"})
