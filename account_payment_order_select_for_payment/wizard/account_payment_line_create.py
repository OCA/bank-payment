# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<https://therp.nl>)
# © 2014-2015 ACSONE SA/NV (<https://acsone.eu>)
# © 2023 Akretion (<https://www.akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountPaymentLineCreate(models.TransientModel):
    _inherit = "account.payment.line.create"

    select_for_payment_filter = fields.Boolean(
        string="Take only to pay",
        store=True,
        readonly=False,
    )

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        context = self.env.context
        order = self.env["account.payment.order"].browse(context["active_id"])
        mode = order.payment_mode_id
        res.update(
            {
                "select_for_payment_filter": mode.default_selected_for_payment,
            }
        )
        return res

    def _prepare_move_line_domain(self):

        res = super()._prepare_move_line_domain()

        if self.select_for_payment_filter:
            res += [("move_id.selected_for_payment", "=", True)]

        return res

    @api.onchange("select_for_payment_filter")
    def move_line_change_select_for_payment_filter(self):
        self.move_line_filters_change()
