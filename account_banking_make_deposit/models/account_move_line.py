# Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
# Copyright (C) 2017 Thinkwell Designs (<http://code.compassfoundation.io>)
# Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    draft_assigned = fields.Boolean(
        'Draft Assigned',
        help=("This field is checked when the move line is assigned "
              "to a draft deposit ticket. The deposit ticket is not "
              "still completely processed"))
    deposit_id = fields.Many2one('deposit.ticket', 'Deposit Ticket')
