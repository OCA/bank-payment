# Copyright Akretion (http://www.akretion.com/)
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    mandate_id = fields.Many2one(
        'account.banking.mandate', string='Direct Debit Mandate',
        ondelete='restrict')

    @api.multi
    def _prepare_payment_line_vals(self, payment_order):
        vals = super(AccountMoveLine, self)._prepare_payment_line_vals(
            payment_order)
        if payment_order.payment_type != 'inbound':
            return vals
        mandate = self.mandate_id
        if not mandate and vals.get('mandate_id', False):
            mandate = mandate.browse(vals['mandate_id'])
        partner_bank_id = vals.get('partner_bank_id', False)
        if not mandate:
            if partner_bank_id:
                domain = [('partner_bank_id', '=', partner_bank_id)]
            else:
                domain = [('partner_id', '=', self.partner_id.id)]
            domain.append(('state', '=', 'valid'))
            mandate = mandate.search(domain, limit=1)
        vals.update({
            'mandate_id': mandate.id,
            'partner_bank_id': mandate.partner_bank_id.id or partner_bank_id,
        })
        return vals

    @api.multi
    @api.constrains('mandate_id', 'company_id')
    def _check_company_constrains(self):
        for ml in self:
            mandate = ml.mandate_id
            if mandate.company_id and mandate.company_id != ml.company_id:
                raise ValidationError(_(
                    "The item %s of journal %s has a different company than "
                    "that of the linked mandate %s).") %
                    (ml.name, ml.move_id.name, ml.mandate_id.display_name))
