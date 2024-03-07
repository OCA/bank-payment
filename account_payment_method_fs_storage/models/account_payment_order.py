# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountPaymentOrder(models.Model):

    _inherit = "account.payment.order"

    def _must_be_exported_to_storage(self):
        self.ensure_one()
        return bool(self.payment_method_id.storage)

    def _export_to_storage(self, file_content, filename):
        storage_id = int(self.payment_method_id.storage)
        # user that confirms order may not have access to storage
        export_storage = self.env["fs.storage"].sudo().search([("id", "=", storage_id)])
        try:
            storage = export_storage._get_filesystem()
            storage.pipe_file(filename, file_content)

        except Exception as e:
            details = str(e) or str(type(e))
            _logger.error(details)
            raise UserError(
                _("Unknown issue to upload the file on the storage:\n{details}").format(
                    details=details
                )
            ) from e
        return True

    def generate_payment_file(self):
        """
        Inherit to catch file generation and put it on the storage (if necessary)
        """
        file_content, filename = super().generate_payment_file()
        if self._must_be_exported_to_storage():
            self._export_to_storage(file_content, filename)
        return file_content, filename

    def open2generated(self):
        self.ensure_one()
        action = super().open2generated()
        if self._must_be_exported_to_storage():
            self.generated2uploaded()
            action = {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "success",
                    "title": _("Generate and export"),
                    "message": _(
                        "The file has been generated and dropped on the storage."
                    ),
                    "sticky": True,
                    "next": {
                        "type": "ir.actions.client",
                        "tag": "reload",
                    },
                },
            }
        return action
