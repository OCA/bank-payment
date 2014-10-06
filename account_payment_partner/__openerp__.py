# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Partner module for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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


{
    'name': 'Account Payment Partner',
    'version': '0.1',
    'category': 'Banking addons',
    'license': 'AGPL-3',
    'summary': 'Adds payment mode on partners and invoices',
    'description': """
Account Payment Partner
=======================

This module adds severals fields :

* the *Supplier Payment Mode* and *Customer Payment Mode* on Partners,

* the *Payment Mode* on Invoices.

On a Payment Order, in the wizard *Select Invoices to Pay*, the invoices will
be filtered per Payment Mode.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'contributors': ['Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>'],
    'depends': ['account_banking_payment_export'],
    'data': [
        'views/res_partner_view.xml',
        'views/account_invoice_view.xml',
    ],
    'demo': ['demo/partner_demo.xml'],
    'installable': True,
}

from openerp import models, fields, api, exceptions
from datetime import datetime


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.one
    @api.constrains('state', 'code')
    def _check_code(self):
        if self.state == 'won':
            if not self.code:
                raise exceptions.Warning('Debe poner un código cuando la etapa se pasa a ganado.')

    @api.constrains('state', 'code')
    def _check_code(self):
        for record in self:
            if record.state == 'won':
                if not record.code:
                    raise exceptions.Warning('Debe poner un código cuando la etapa se pasa a ganado.')

    def do_something(self, vals):
        pass

    def create(self, vals):
        # Complementar valores del create
        rec_id = super(CrmLead, self).create(vals)
        # Crear registros accesorios
        analytic_acc_obj = self.env['account.analytic.account']
        analytic_acc_obj.create({'name': vals['name'],
                                 'type': 'project',
                                 'date': datetime.now(),
                                 'project_id': rec_id})
        analytic_accs = analytic_acc_obj.search([('type', '=', 'project')],
                                                order='partner_id', limit=1)
        analytic_accs.write({'partner_id': 1})
        return rec_id

    def copy(self, default):
        default['name'] = self.name + " (copia)"
        return super(CrmLead, self).copy(default)

    def search(self, domain):
        return {1: {''}, 2: {} }

    @api.one
    def unlink(self):
        if self.state in ('to_invoice', 'done'):
            raise exceptions.Warning('No se puede borrar un pedido confirmado.')
        super(CrmLead, self).unlink()
        return True

    def write(self, vals):
        if vals.get('state') == 'won':
            for record in self:
                if not record.code and not vals.get('code'):
                    raise exceptions.Warning('Debe poner un código cuando la etapa se pasa a ganado.')
        return super(CrmLead, self).write(vals)
