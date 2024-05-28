# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends(
        "partner_id", "partner_invoice_id", "partner_shipping_id", "payment_mode_id"
    )
    def _compute_mandate_id(self):
        procesed_orders = self.browse()
        for order in self:
            if (
                order.partner_invoice_id
                and order.payment_mode_id
                and order.payment_mode_id.payment_method_id.mandate_required
            ):
                partner_mandate_config = (
                    order.commercial_invoice_partner_id.sale_default_mandate_contact
                    or order.company_id.sale_default_mandate_contact
                )
                if partner_mandate_config:
                    mandate = False
                    if partner_mandate_config == "partner_id":
                        mandate = order.partner_id.contact_mandate_id
                    if partner_mandate_config == "commercial_partner_id":
                        mandate = (
                            order.partner_id.commercial_partner_id.contact_mandate_id
                        )
                    elif partner_mandate_config == "partner_invoice_id":
                        mandate = order.partner_invoice_id.contact_mandate_id
                    elif partner_mandate_config == "partner_shipping_id":
                        mandate = order.partner_shipping_id.contact_mandate_id
                    if mandate:
                        order.mandate_id = mandate
                        procesed_orders |= order
        return super(SaleOrder, self - procesed_orders)._compute_mandate_id()
