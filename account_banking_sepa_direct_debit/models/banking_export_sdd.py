# -*- encoding: utf-8 -*-
##############################################################################
#
#    SEPA Direct Debit module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp
from unidecode import unidecode


class BankingExportSdd(models.Model):
    """SEPA Direct Debit export"""
    _name = 'banking.export.sdd'
    _description = __doc__
    _rec_name = 'filename'

    @api.one
    @api.depends('payment_order_ids', 'payment_order_ids.reference')
    def _generate_filename(self):
        if self.payment_order_ids:
            ref = self.payment_order_ids[0].reference
            label = unidecode(ref.replace('/', '-')) if ref else 'error'
            filename = 'sdd_%s.xml' % label
        else:
            filename = 'sdd.xml'
        self.filename = filename

    payment_order_ids = fields.Many2many(
        comodel_name='payment.order',
        relation='account_payment_order_sdd_rel',
        column1='banking_export_sepa_id', column2='account_order_id',
        string='Payment Orders',
        readonly=True)
    nb_transactions = fields.Integer(
        string='Number of Transactions', readonly=True)
    total_amount = fields.Float(
        string='Total Amount', digits_compute=dp.get_precision('Account'),
        readonly=True)
    batch_booking = fields.Boolean(
        'Batch Booking', readonly=True,
        help="If true, the bank statement will display only one credit line "
             "for all the direct debits of the SEPA file ; if false, the bank "
             "statement will display one credit line per direct debit of the "
             "SEPA file.")
    charge_bearer = fields.Selection(
        [('SLEV', 'Following Service Level'),
         ('SHAR', 'Shared'),
         ('CRED', 'Borne by Creditor'),
         ('DEBT', 'Borne by Debtor')], 'Charge Bearer', readonly=True,
        help="Following service level : transaction charges are to be applied "
             "following the rules agreed in the service level and/or scheme "
             "(SEPA Core messages must use this). Shared : transaction "
             "charges on the creditor side are to be borne by the creditor, "
             "transaction charges on the debtor side are to be borne by the "
             "debtor. Borne by creditor : all transaction charges are to be "
             "borne by the creditor. Borne by debtor : all transaction "
             "charges are to be borne by the debtor.")
    create_date = fields.Datetime(string='Generation Date', readonly=True)
    file = fields.Binary(string='SEPA File', readonly=True)
    filename = fields.Char(compute=_generate_filename, size=256,
                           string='Filename', readonly=True, store=True)
    state = fields.Selection([('draft', 'Draft'), ('sent', 'Sent')],
                             string='State', readonly=True, default='draft')
