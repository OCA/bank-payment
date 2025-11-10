# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def _action_send_mail(self, auto_commit=False):
        for wizard in self:
            if self.env.context.get("is_sent"):
                self.env[wizard.model].sudo().browse(
                    json.loads(wizard.res_ids)
                ).is_sent = True
        return super()._action_send_mail(auto_commit=auto_commit)
