# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Uninstall account_payment_method_fs_storage ")
    cr.execute(
        """
      UPDATE ir_module_module
      SET state='to remove'
      WHERE name = 'account_payment_method_fs_storage'
      AND state IN ('installed', 'to upgrade', 'to install')
      """
    )
