from secrets import token_urlsafe

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    plaid_token = fields.Char(copy=False, groups="base.group_user")

    def _ensure_plaid_token(self):
        for partner in self:
            if not partner.plaid_token:
                partner.plaid_token = token_urlsafe(32)
        return True

    def _get_plaid_portal_link(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        return f"{base_url}/bank/connect/{self.plaid_token}"

    plaid_portal_link = fields.Char(
        string="Plaid portal link", compute="_compute_portal_link"
    )

    @api.depends("plaid_token")
    def _compute_portal_link(self):
        for partner in self:
            partner.plaid_portal_link = (
                partner._get_plaid_portal_link() if partner.plaid_token else False
            )

    def action_send_plaid_email(self):
        self.ensure_one()
        if not self.email:
            raise UserError(_("The partner must have an email."))
        self._ensure_plaid_token()
        template = self.env.ref(
            "account_payment_plaid.mail_template_partner_plaid_invite"
        )
        template.send_mail(self.id, force_send=True)

    def action_server_send_plaid_email(self):
        template = self.env.ref(
            "account_payment_plaid.mail_template_partner_plaid_invite"
        )
        missing = []

        for partner in self:
            if not partner.email:
                missing.append(partner.name)
                continue
            partner._ensure_plaid_token()
            template.send_mail(partner.id, force_send=True)

        if missing:
            raise UserError(
                _("The following partners are missing an email address:\n%s")
                % "\n".join(missing)
            )
