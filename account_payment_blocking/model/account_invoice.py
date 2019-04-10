# -*- coding: utf-8 -*-
# Copyright 2014-2015 ACSONE SA/NV (http://acsone.eu)
# Author: Adrien Peiffer <adrien.peiffer@acsone.eu>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, models, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _get_move_line(self, invoice_id):
        return self.env['account.move.line'].search([
            ('account_id.type', 'in', ['payable', 'receivable']),
            ('invoice.id', '=', invoice_id)
        ]).ids

    @api.model
    def _update_blocked(self, invoice, value):
        if invoice.move_id:
            move_line_ids = self._get_move_line(invoice.id)
            self.env['account.move.line'].with_context(
                # work with account_constraints from OCA/AFT
                from_parent_object=True
            ).browse(move_line_ids).write({'blocked': value})

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        for invoice in self:
            self._update_blocked(invoice, invoice.draft_blocked)
        return res

    @api.multi
    @api.depends('move_id.line_id.blocked')
    def _compute_blocked(self):
        for invoice in self:
            if invoice.move_id:
                move_line_ids = self._get_move_line(invoice.id)
                move_lines = self.env['account.move.line']\
                    .browse(move_line_ids)
                invoice.blocked = move_lines and\
                    all(line.blocked for line in move_lines) or False
            else:
                invoice.blocked = False

    @api.model
    def _search_blocked(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value) or (
                operator in ('<>', '!=') and not value):
            search_operator = 'in'
        else:
            search_operator = 'not in'
        self.env.cr.execute('''
            select distinct i.id
            from
                account_move_line ml,
                account_move m,
                account_invoice i,
                account_account a
            where ml.move_id = m.id
                and i.move_id = m.id
                and ml.account_id = a.id
                and ml.blocked = 't'
                and a.type in ('receivable', 'payable')
        ''')
        res_ids = [x[0] for x in self.env.cr.fetchall()]
        return [('id', search_operator, res_ids)]

    @api.multi
    def _inverse_blocked(self):
        for invoice in self:
            self._update_blocked(invoice, invoice.blocked)

    blocked = fields.Boolean(
        compute='_compute_blocked',
        inverse='_inverse_blocked',
        string='No Follow Up',
        states={'draft': [('readonly', True)]},
        search='_search_blocked',
    )
    draft_blocked = fields.Boolean(string='No Follow Up')
