# Copyright 2020 Akretion - Alexis de Lattre
# Copyright 2014 Tecnativa - Pedro M. Baeza
# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

NUMBER_OF_UNUSED_MONTHS_BEFORE_EXPIRY = 36

logger = logging.getLogger(__name__)


class AccountBankingMandate(models.Model):
    """SEPA Direct Debit Mandate"""

    _inherit = "account.banking.mandate"
    _rec_name = "display_name"

    format = fields.Selection(
        selection_add=[("sepa", "Sepa Mandate")],
        default="sepa",
        ondelete={"sepa": "set default"},
    )
    type = fields.Selection(
        selection_add=[("recurrent", "Recurrent"), ("oneoff", "One-Off")],
        default="recurrent",
        ondelete={"recurrent": "set null", "oneoff": "set null"},
    )
    recurrent_sequence_type = fields.Selection(
        [("first", "First"), ("recurring", "Recurring"), ("final", "Final")],
        string="Sequence Type for Next Debit",
        tracking=70,
        help="This field is only used for Recurrent mandates, not for "
        "One-Off mandates.",
        default="first",
    )
    scheme = fields.Selection(
        [("CORE", "Basic (CORE)"), ("B2B", "Enterprise (B2B)")],
        default="CORE",
        tracking=80,
    )
    unique_mandate_reference = fields.Char(size=35)  # cf ISO 20022
    display_name = fields.Char(compute="_compute_display_name2", store=True)
    is_sent = fields.Boolean()

    @api.constrains("type", "recurrent_sequence_type")
    def _check_recurring_type(self):
        for mandate in self:
            if mandate.type == "recurrent" and not mandate.recurrent_sequence_type:
                raise UserError(
                    _("The recurrent mandate '%s' must have a sequence type.")
                    % mandate.unique_mandate_reference
                )

    @api.depends("unique_mandate_reference", "recurrent_sequence_type")
    def _compute_display_name2(self):
        for mandate in self:
            if mandate.format == "sepa":
                mandate.display_name = (
                    f"{mandate.unique_mandate_reference} "
                    f"({mandate.recurrent_sequence_type})"
                )
            else:
                mandate.display_name = mandate.unique_mandate_reference

    @api.onchange("partner_bank_id")
    def mandate_partner_bank_change(self):
        super().mandate_partner_bank_change()
        res = {}
        if (
            self.state == "valid"
            and self.partner_bank_id
            and self.type == "recurrent"
            and self.recurrent_sequence_type != "first"
        ):
            self.recurrent_sequence_type = "first"
            res["warning"] = {
                "title": _("Mandate update"),
                "message": _(
                    "As you changed the bank account attached "
                    "to this mandate, the 'Sequence Type' has "
                    "been set back to 'First'."
                ),
            }
        return res

    def _sdd_mandate_set_state_to_expired(self):
        logger.info("Searching for SDD Mandates that must be set to Expired")
        expire_limit_date = datetime.today() + relativedelta(
            months=-NUMBER_OF_UNUSED_MONTHS_BEFORE_EXPIRY
        )
        expired_mandates = self.search(
            [
                "|",
                ("last_debit_date", "=", False),
                ("last_debit_date", "<=", expire_limit_date),
                ("state", "=", "valid"),
                ("signature_date", "<=", expire_limit_date),
            ]
        )
        if expired_mandates:
            expired_mandates.write({"state": "expired"})
            for mandate in expired_mandates:
                mandate.message_post(
                    body=_(
                        "Mandate automatically set to"
                        " expired after %d months without use."
                    )
                    % NUMBER_OF_UNUSED_MONTHS_BEFORE_EXPIRY
                )
            logger.info(
                "%d SDD Mandate set to expired: IDs %s"
                % (len(expired_mandates), expired_mandates.ids)
            )
        else:
            logger.info("0 SDD Mandates had to be set to Expired")

    def print_report(self):
        self.ensure_one()
        xmlid = "account_banking_sepa_direct_debit.report_sepa_direct_debit_mandate"
        action = self.env.ref(xmlid).report_action(self)
        return action

    def action_mandate_send(self):
        """Opens a wizard to compose an email,
        with relevant mail template loaded by default"""
        self.ensure_one()
        template_id = self.env["ir.model.data"]._xmlid_to_res_id(
            "account_banking_sepa_direct_debit.email_template_sepa_mandate",
            raise_if_not_found=False,
        )
        ctx = {
            "default_model": "account.banking.mandate",
            "default_res_ids": self.ids,
            "default_use_template": bool(template_id),
            "default_template_id": template_id,
            "default_composition_mode": "comment",
            "is_sent": True,
            "force_email": True,
        }
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "view_id": False,
            "target": "new",
            "context": ctx,
        }
