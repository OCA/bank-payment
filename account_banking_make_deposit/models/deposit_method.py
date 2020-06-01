# Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
# Copyright (C) 2017 Thinkwell Designs (<http://code.compassfoundation.io>)
# Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class DepositMethod(models.Model):
    _name = "deposit.method"
    _description = "Deposit Method"

    name = fields.Char(string="Name", translate=True,
                       help="Name of the method used to deposit")
