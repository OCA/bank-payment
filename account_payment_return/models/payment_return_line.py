# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011-2012 7 i TRIA <http://www.7itria.cat>
#    Copyright (c) 2011-2012 Avanzosc <http://www.avanzosc.com>
#    Copyright (c) 2013 Serv. Tecnol. Avanzados <http://www.serviciosbaeza.com>
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#    Copyright (c) 2014 initOS GmbH & Co. KG <http://initos.com/>
#                       Markus Schneider <markus.schneider at initos.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class PaymentReturnLine(models.Model):
    _name = "payment.return.line"
    _description = 'Payment return lines'

    return_id = fields.Many2one('payment.return', 'Payment return',
                                required=True, ondelete='cascade')
    concept = fields.Char('Concept',
                          help="Readed from imported file. "
                          "Only for reference.")
    reason = fields.Char('Return reason',
                         help="Readed from imported file. "
                         "Only for reference.")
    move_line_id = fields.Many2one(
        'account.move.line', 'Payment Reference')
    date = fields.Date('Return date',
                       help="Readed from imported file. "
                       "Only for reference.",
                       default=lambda *x: fields.Date.today())
    notes = fields.Text('Notes')
    partner_name = fields.Char('Partner name',
                               help="Readed from imported file. "
                               "Only for reference.")
    partner_id = fields.Many2one('res.partner', 'Customer',
                                 domain="[('customer', '=', True)]")
    amount = fields.Float('Amount',
                          help="Returned amount. Can be different from "
                          "the move amount",
                          digits_compute=dp.get_precision('Account'))
    reconcile_id = fields.Many2one('account.move.reconcile', 'Reconcile',
                                   help="Reference to the "
                                   "reconcile object.")

    @api.onchange('move_line_id')
    def onchange_move_line(self):
        self.amount = self.move_line_id.credit
