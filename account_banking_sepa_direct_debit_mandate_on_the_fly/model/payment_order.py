# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from datetime import datetime
from openerp.osv.orm import Model
from openerp.osv import fields
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class PaymentOrder(Model):
    _inherit = 'payment.order'

    def _is_missing_mandates_get(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for this in self.browse(cr, uid, ids, context=context):
            if this.payment_order_type != 'debit':
                result[this.id] = False
                continue
            result[this.id] = any(
                [not l.sdd_mandate_id for l in this.line_ids])
        return result

    _columns = {
        'is_missing_mandates': fields.function(
            _is_missing_mandates_get, type='boolean',
            string='Is missing mandates'),
    }

    def button_create_missing_sdd_mandates(self, cr, uid, ids, context=None):
        sdd_mandate = self.pool['sdd.mandate']
        sdd_type = self.pool['ir.config_parameter'].get_param(
            cr, uid, 'account.banking.sepa.direct.debit.create.mandates',
            'oneoff', context=context)
        for this in self.browse(cr, uid, ids, context=context):
            for line in this.line_ids:
                if line.sdd_mandate_id:
                    continue
                mandate_id = sdd_mandate.create(
                    cr, uid,
                    {
                        'type': sdd_type,
                        'recurrent_sequence_type': 'first'
                            if sdd_type == 'recurrent' else False,
                        'sepa_migrated': True,
                        'signature_date': datetime.today().strftime(
                            DEFAULT_SERVER_DATE_FORMAT),
                        'partner_bank_id': line.bank_id.id,
                        'partner_id': line.partner_id.id,
                    },
                    context=context)
                sdd_mandate.validate(cr, uid, [mandate_id], context=context)
                line.write({'sdd_mandate_id': mandate_id})
        return {}
