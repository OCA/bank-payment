# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def _action_send_mail(self, auto_commit=False):
        for wizard in self:
            if self.env.context.get("is_sent"):
                self.env[wizard.model].sudo().browse(wizard.res_id).is_sent = True
        return super(MailComposeMessage, self)._action_send_mail(
            auto_commit=auto_commit
        )
