# Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
# Copyright (C) 2017 Thinkwell Designs (<http://code.compassfoundation.io>)
# Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class DepositTicketLine(models.Model):
    _name = 'deposit.ticket.line'
    _description = 'Deposit Ticket Line'

    name = fields.Char('Name', size=64, required=True,
                       help='Derived from the related Journal Item.')
    ref = fields.Char('Reference', size=64, required=True,
                      help='Derived from the related Journal Item.')
    date = fields.Date('Date', required=True,
                       help='Derived from the related Journal Item')
    partner_id = fields.Many2one(
        'res.partner', 'Partner',
        help='Derived from the related Journal Item.')
    amount = fields.Float(
        'Amount', digits=dp.get_precision('Account'),
        help="Derived from the 'debit' amount from related Journal Item.")
    deposit_id = fields.Many2one(
        'deposit.ticket', 'Deposit Ticket', required=True, ondelete='cascade')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, readonly=True,
        help="The Company for which the deposit ticket is made to",
    )
    move_line_id = fields.Many2one(
        'account.move.line', 'Journal Item',
        help='Related Journal Item')
    currency_id = fields.Many2one('res.currency', 'Currency')

    @api.onchange('deposit_id')
    def onchange_deposit_id(self):
        self.company_id = self.deposit_id.company_id.id
        self.currency_id = self.company_id.currency_id

    @api.onchange('deposit_id')
    def onchange_date(self):
        self.date = self.deposit_id.date

    @api.model
    def create(self, vals):
        # Any Line cannot be manually added. Use the wizard to add lines.
        if not vals.get('move_line_id', False):
            raise UserError(_(
                "You cannot add any new deposit ticket line manually as of "
                "this revision! Please use the button 'Add Deposit Items' to "
                "add deposit ticket line!"))
        return super(DepositTicketLine, self).create(vals)

    @api.multi
    def unlink(self):
        """
        Set the 'draft_assigned' field to False for related account move
        lines to allow to be entered for another deposit.
        """
        move_lines = [line.move_line_id for line in self]
        for move_line in move_lines:
            move_line.write({'draft_assigned': False})
        return super(DepositTicketLine, self).unlink()
