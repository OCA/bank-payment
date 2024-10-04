# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    property_account_receivable_id = fields.Many2one(
        company_dependent=False,
        compute="_compute_property_account_receivable_id",
        inverse="_inverse_property_account_receivable_id",
    )

    property_stored_account_receivable_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Account Receivable",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",  # noqa
    )

    property_account_payable_id = fields.Many2one(
        company_dependent=False,
        compute="_compute_property_account_payable_id",
        inverse="_inverse_property_account_payable_id",
    )

    property_stored_account_payable_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Account Payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",  # noqa
    )

    @api.depends("property_stored_account_receivable_id")
    @api.depends_context("_partner_property_account_payment_mode")
    def _compute_property_account_receivable_id(self):
        payment_mode_id = self.env.context.get("_partner_property_account_payment_mode")
        if payment_mode_id:
            payment_mode = self.env["account.payment.mode"].browse(payment_mode_id)
            rec_account = payment_mode.default_receivable_account_id
            if rec_account:
                self.update({"property_account_receivable_id": rec_account})
                return
        for partner in self:
            partner.property_account_receivable_id = (
                partner.property_stored_account_receivable_id
            )

    def _inverse_property_account_receivable_id(self):
        for partner in self:
            partner.property_stored_account_receivable_id = (
                partner.property_account_receivable_id
            )

    @api.depends("property_stored_account_payable_id")
    @api.depends_context("_partner_property_account_payment_mode")
    def _compute_property_account_payable_id(self):
        payment_mode_id = self.env.context.get("_partner_property_account_payment_mode")
        if payment_mode_id:
            payment_mode = self.env["account.payment.mode"].browse(payment_mode_id)
            rec_account = payment_mode.default_payable_account_id
            if rec_account:
                self.update({"property_account_payable_id": rec_account})
                return
        for partner in self:
            partner.property_account_payable_id = (
                partner.property_stored_account_payable_id
            )

    def _inverse_property_account_payable_id(self):
        for partner in self:
            partner.property_stored_account_payable_id = (
                partner.property_account_payable_id
            )
