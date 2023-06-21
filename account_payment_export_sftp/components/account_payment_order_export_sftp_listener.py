# Copyright 2023 Compassion CH
# @author: Simon Gonzalez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class EdiOutputGenerateDDSFTP(Component):
    _name = "edi.output.generate.dd_sftp"
    _inherit = "base.event.listener"
    _apply_on = ["account.payment.order"]

    def _get_exchange_record_vals(self, record):
        return {
            "model": record._name,
            "res_id": record.id,
            "exchange_file": self.env.context.get("exchange_file", False),
            "exchange_filename": self.env.context.get("exchange_filename", False),
        }

    def on_file_generation_payment_order(self, records):
        for record in records:
            if record.disable_edi_auto:
                continue
            backend = record.edi_exchange_type_id.backend_id
            if not backend:
                continue
            exchange_type = record.edi_exchange_type_id
            if record._has_exchange_record(exchange_type, backend):
                continue
            exchange_record = backend.create_record(
                exchange_type.code, self._get_exchange_record_vals(record)
            )
            if exchange_record.exchange_file:
                exchange_record.edi_exchange_state = "output_pending"
                exchange_record.with_delay().action_exchange_send()
            else:
                exchange_record.with_delay().action_exchange_generate()
