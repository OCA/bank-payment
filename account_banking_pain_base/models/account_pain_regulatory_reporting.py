# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountPainRegulatoryReporting(models.Model):
    _name = "account.pain.regulatory.reporting"
    _description = "Regulatory Reporting Codes for ISO 20022/PAIN banking standard"
    _order = "code, country_id"

    code = fields.Char(required=True, copy=False, size=10)
    name = fields.Char(required=True, translate=True, copy=False)
    country_id = fields.Many2one("res.country", ondelete="restrict", required=False)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "code_country_unique",
            "unique(code, country_id)",
            "This code already exists for that country.",
        )
    ]

    @api.depends("code", "name")
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, "[%s] %s" % (rec.code, rec.name)))
        return res

    def _name_search(
        self, name="", args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        if args is None:
            args = []
        ids = []
        if name and operator == "ilike":
            ids = list(self._search([("code", "=", name)] + args, limit=limit))
            if ids:
                return ids
        return super()._name_search(
            name=name,
            args=args,
            operator=operator,
            limit=limit,
            name_get_uid=name_get_uid,
        )
