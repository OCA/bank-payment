# Copyright 2022 Akretion France (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Iso20022CodeList(models.Model):
    _name = "iso20022.code.list"
    _description = "ISO 20022 Code lists"
    _order = "field, code"

    code = fields.Char(required=True, copy=False, help="The code mustn't be modified.")
    name = fields.Char(required=True, copy=False)
    field = fields.Selection(
        [
            ("purpose", "Purpose"),
            ("category_purpose", "Category Purpose"),
        ],
        required=True,
        index=True,
    )
    description = fields.Text(copy=False)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "field_code_uniq",
            "unique(field, code)",
            "This code already exists for this field.",
        )
    ]

    @api.depends("code", "name")
    def name_get(self):
        res = []
        for entry in self:
            res.append((entry.id, "[{}] {}".format(entry.code, entry.name)))
        return res

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if args is None:
            args = []
        if name and operator == "ilike":
            recs = self.search([("code", "=", name)] + args, limit=limit)
            if recs:
                return recs.name_get()
        return super().name_search(name=name, args=args, operator=operator, limit=limit)
