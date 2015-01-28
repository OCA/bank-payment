# -*- encoding: utf-8 -*-
##############################################################################
#
#    SEPA Credit Transfer module for OpenERP
#    Copyright (C) 2010-2013 Akretion (http://www.akretion.com)
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

try:
    from unidecode import unidecode
except ImportError:
    unidecode = None


class BankingExportSepa(models.Model):
    """SEPA export"""
    _name = 'banking.export.sepa'
    _description = __doc__
    _rec_name = 'filename'

    @api.one
    def _generate_filename(self):
        ref = self.payment_order_ids.reference
        if ref:
            label = unidecode(ref.replace('/', '-'))
        else:
            label = 'error'
        self.filename = 'sct_%s.xml' % label

    payment_order_ids = fields.Many2many(
        comodel_name='payment.order', column1='banking_export_sepa_id',
        column2='account_order_id', relation='account_payment_order_sepa_rel',
        string='Payment Orders', readonly=True)
    nb_transactions = fields.Integer(string='Number of Transactions',
                                     readonly=True)
    total_amount = fields.Float(string='Total Amount',
                                digits_compute=dp.get_precision('Account'),
                                readonly=True)
    batch_booking = fields.Boolean(
        'Batch Booking', readonly=True,
        help="If true, the bank statement will display only one debit line "
             "for all the wire transfers of the SEPA XML file ; if false, "
             "the bank statement will display one debit line per wire "
             "transfer of the SEPA XML file.")
    charge_bearer = fields.Selection(
        [('SLEV', 'Following Service Level'),
         ('SHAR', 'Shared'),
         ('CRED', 'Borne by Creditor'),
         ('DEBT', 'Borne by Debtor')], string='Charge Bearer', readonly=True,
        help="Following service level : transaction charges are to be applied "
             "following the rules agreed in the service level and/or scheme "
             "(SEPA Core messages must use this). Shared : transaction "
             "charges on the creditor side are to be borne by the creditor, "
             "transaction charges on the debtor side are to be borne by the "
             "debtor. Borne by creditor : all transaction charges are to be "
             "borne by the creditor. Borne by debtor : all transaction "
             "charges are to be borne by the debtor.")
    create_date = fields.Datetime('Generation Date', readonly=True)
    file = fields.Binary('SEPA XML File', readonly=True)
    filename = fields.Char(string='Filename', size=256, readonly=True,
                           compute=_generate_filename)
    state = fields.Selection([('draft', 'Draft'), ('sent', 'Sent')],
                             string='State', readonly=True, default='draft')
