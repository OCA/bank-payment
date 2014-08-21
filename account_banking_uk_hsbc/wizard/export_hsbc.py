# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#    Copyright (C) 2011 credativ Ltd (<http://www.credativ.co.uk>).
#    All Rights Reserved
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

import base64
from datetime import datetime, date
from decimal import Decimal
import paymul
import string
import random
import logging

from openerp.osv import orm, fields
from openerp.tools import ustr
from openerp.tools.translate import _


def strpdate(arg, format='%Y-%m-%d'):
    """shortcut"""
    return datetime.strptime(arg, format).date()


def strfdate(arg, format='%Y-%m-%d'):
    """shortcut"""
    return arg.strftime(format)


class banking_export_hsbc_wizard(orm.TransientModel):
    _name = 'banking.export.hsbc.wizard'
    _description = 'HSBC Export'
    _columns = {
        'state': fields.selection(
            [
                ('create', 'Create'),
                ('finish', 'Finish')
            ],
            'State',
            readonly=True,
        ),
        'test': fields.boolean(),
        'reference': fields.char(
            'Reference', size=35,
            help=('The bank will use this reference in feedback communication '
                  'to refer to this run. 35 characters are available.'
                  ),
            ),
        'execution_date_create': fields.date(
            'Execution Date',
            help=('This is the date the file should be processed by the bank. '
                  'Don\'t choose a date beyond the nearest date in your '
                  'payments. The latest allowed date is 30 days from now.\n'
                  'Please keep in mind that banks only execute on working '
                  'days and typically use a delay of two days between '
                  'execution date and effective transfer date.'
                  ),
            ),
        'file_id': fields.many2one(
            'banking.export.hsbc',
            'hsbc File',
            readonly=True
            ),
        'file': fields.related(
            'file_id', 'file', type='binary',
            readonly=True,
            string='File',
            ),
        'execution_date_finish': fields.related(
            'file_id', 'execution_date', type='date',
            readonly=True,
            string='Execution Date',
            ),
        'total_amount': fields.related(
            'file_id', 'total_amount',
            type='float',
            string='Total Amount',
            readonly=True,
            ),
        'no_transactions': fields.integer(
            'Number of Transactions',
            readonly=True,
            ),
        'payment_order_ids': fields.many2many(
            'payment.order', 'rel_wiz_payorders', 'wizard_id',
            'payment_order_id', 'Payment Orders',
            readonly=True,
            ),
        }

    logger = logging.getLogger('export_hsbc')

    def create(self, cursor, uid, wizard_data, context=None):
        '''
        Retrieve a sane set of default values based on the payment orders
        from the context.
        '''

        if 'execution_date_create' not in wizard_data:
            po_ids = context.get('active_ids', [])
            po_model = self.pool.get('payment.order')
            pos = po_model.browse(cursor, uid, po_ids)

            execution_date = date.today()

            for po in pos:
                if po.date_prefered == 'fixed' and po.date_planned:
                    execution_date = strpdate(po.date_planned)
                elif po.date_prefered == 'due':
                    for line in po.line_ids:
                        if line.move_line_id.date_maturity:
                            date_maturity = strpdate(
                                line.move_line_id.date_maturity
                            )
                            if date_maturity < execution_date:
                                execution_date = date_maturity

            execution_date = max(execution_date, date.today())

            # The default reference contains a /, which is invalid for PAYMUL
            reference = pos[0].reference.replace('/', ' ')

            wizard_data.update({
                'execution_date_create': strfdate(execution_date),
                'reference': reference,
                'payment_order_ids': [(6, 0, po_ids)],
                'state': 'create',
            })

        return super(banking_export_hsbc_wizard, self).create(
            cursor, uid, wizard_data, context)

    def _create_account(self, oe_account, origin_country=None,
                        is_origin_account=False):
        # let the receiving bank select the currency from the batch
        currency = None
        holder = oe_account.owner_name or oe_account.partner_id.name
        self.logger.info('Create account %s' % (holder))
        self.logger.info('-- %s' % (oe_account.country_id.code))
        self.logger.info('-- %s' % (oe_account.acc_number))

        if oe_account.state == 'iban':
            self.logger.info('IBAN: %s' % (oe_account.acc_number))
            paymul_account = paymul.IBANAccount(
                iban=oe_account.acc_number,
                bic=oe_account.bank.bic,
                holder=holder,
                currency=currency,
            )
            transaction_kwargs = {
                'charges': paymul.CHARGES_EACH_OWN,
            }
        elif oe_account.country_id.code == 'GB':
            self.logger.info('GB: %s %s' % (oe_account.country_id.code,
                                            oe_account.acc_number))
            split = oe_account.acc_number.split(" ", 2)
            if len(split) == 2:
                sortcode, accountno = split
            else:
                raise orm.except_orm(
                    _('Error'),
                    "Invalid GB acccount number '%s'" % oe_account.acc_number)
            paymul_account = paymul.UKAccount(
                number=accountno,
                sortcode=sortcode,
                holder=holder,
                currency=currency,
            )
            transaction_kwargs = {
                'charges': paymul.CHARGES_PAYEE,
            }
        elif oe_account.country_id.code in ('US', 'CA'):
            self.logger.info('US/CA: %s %s' % (oe_account.country_id.code,
                                               oe_account.acc_number))
            split = oe_account.acc_number.split(' ', 2)
            if len(split) == 2:
                sortcode, accountno = split
            else:
                raise orm.except_orm(
                    _('Error'),
                    _("Invalid %s account number '%s'") %
                    (oe_account.country_id.code, oe_account.acc_number))
            paymul_account = paymul.NorthAmericanAccount(
                number=accountno,
                sortcode=sortcode,
                holder=holder,
                currency=currency,
                swiftcode=oe_account.bank.bic,
                country=oe_account.country_id.code,
                origin_country=origin_country,
                is_origin_account=is_origin_account
            )
            transaction_kwargs = {
                'charges': paymul.CHARGES_PAYEE,
            }
            transaction_kwargs = {
                'charges': paymul.CHARGES_PAYEE,
            }
        else:
            self.logger.info('SWIFT Account: %s' % oe_account.country_id.code)
            split = oe_account.acc_number.split(' ', 2)
            if len(split) == 2:
                sortcode, accountno = split
            else:
                raise orm.except_orm(
                    _('Error'),
                    _("Invalid %s account number '%s'") %
                    (oe_account.country_id.code, oe_account.acc_number))
            paymul_account = paymul.SWIFTAccount(
                number=accountno,
                sortcode=sortcode,
                holder=holder,
                currency=currency,
                swiftcode=oe_account.bank.bic,
                country=oe_account.country_id.code,
            )
            transaction_kwargs = {
                'charges': paymul.CHARGES_PAYEE,
            }
            transaction_kwargs = {
                'charges': paymul.CHARGES_PAYEE,
            }

        return paymul_account, transaction_kwargs

    def _create_transaction(self, line):
        # Check on missing partner of bank account (this can happen!)
        if not line.bank_id or not line.bank_id.partner_id:
            raise orm.except_orm(
                _('Error'),
                _('There is insufficient information.\r\n'
                  'Both destination address and account '
                  'number must be provided')
            )

        self.logger.info('====')
        dest_account, transaction_kwargs = self._create_account(
            line.bank_id, line.order_id.mode.bank_id.country_id.code
        )

        means = {
            'ACH or EZONE': paymul.MEANS_ACH_OR_EZONE,
            'Faster Payment': paymul.MEANS_FASTER_PAYMENT,
            'Priority Payment': paymul.MEANS_PRIORITY_PAYMENT
        }.get(line.order_id.mode.type.name)
        if means is None:
            raise orm.except_orm(
                _('Error'),
                _("Invalid payment type mode for HSBC '%s'")
                % line.order_id.mode.type.name
            )

        if not line.info_partner:
            raise orm.except_orm(
                _('Error'),
                _("No default address for transaction '%s'") % line.name
            )

        try:
            return paymul.Transaction(
                amount=Decimal(str(line.amount_currency)),
                currency=line.currency.name,
                account=dest_account,
                means=means,
                name_address=line.info_partner,
                customer_reference=line.name,
                payment_reference=line.name,
                **transaction_kwargs
            )
        except ValueError as exc:
            raise orm.except_orm(
                _('Error'),
                _('Transaction invalid: %s') + ustr(exc)
            )

    def wizard_export(self, cursor, uid, wizard_data_ids, context):
        '''
        Wizard to actually create the HSBC file
        '''

        wizard_data = self.browse(cursor, uid, wizard_data_ids, context)[0]
        result_model = self.pool.get('banking.export.hsbc')
        payment_orders = wizard_data.payment_order_ids

        try:
            self.logger.info(
                'Source - %s (%s) %s' % (
                    payment_orders[0].mode.bank_id.partner_id.name,
                    payment_orders[0].mode.bank_id.acc_number,
                    payment_orders[0].mode.bank_id.country_id.code)
            )
            src_account = self._create_account(
                payment_orders[0].mode.bank_id,
                payment_orders[0].mode.bank_id.country_id.code,
                is_origin_account=True
            )[0]
        except ValueError as exc:
            raise orm.except_orm(
                _('Error'),
                _('Source account invalid: ') + ustr(exc)
            )

        if not isinstance(src_account, paymul.UKAccount):
            raise orm.except_orm(
                _('Error'),
                _("Your company's bank account has to have a valid UK "
                  "account number (not IBAN)" + ustr(type(src_account)))
            )

        try:
            self.logger.info('Create transactions...')
            transactions = []
            hsbc_clientid = ''
            for po in payment_orders:
                transactions += [
                    self._create_transaction(l) for l in po.line_ids
                ]
                hsbc_clientid = po.hsbc_clientid_id.clientid

            batch = paymul.Batch(
                exec_date=strpdate(wizard_data.execution_date_create),
                reference=wizard_data.reference,
                debit_account=src_account,
                name_address=payment_orders[0].line_ids[0].info_owner,
            )
            batch.transactions = transactions
        except ValueError as exc:
            raise orm.except_orm(
                _('Error'),
                _('Batch invalid: ') + ustr(exc)
            )

        # Generate random identifier until an unused one is found
        while True:
            ref = ''.join(random.choice(string.ascii_uppercase + string.digits)
                          for x in range(15))

            ids = result_model.search(cursor, uid, [
                ('identification', '=', ref)
            ])

            if not ids:
                break

        message = paymul.Message(reference=ref)
        message.batches.append(batch)
        interchange = paymul.Interchange(client_id=hsbc_clientid,
                                         reference=ref,
                                         message=message)

        export_result = {
            'identification': interchange.reference,
            'execution_date': batch.exec_date,
            'total_amount': batch.amount(),
            'no_transactions': len(batch.transactions),
            'file': base64.encodestring(str(interchange)),
            'payment_order_ids': [
                [6, 0, [po.id for po in payment_orders]]
            ],
        }
        file_id = result_model.create(cursor, uid, export_result, context)

        self.write(cursor, uid, [wizard_data_ids[0]], {
            'file_id': file_id,
            'no_transactions': len(batch.transactions),
            'state': 'finish',
        }, context)

        return {
            'name': _('HSBC Export'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'domain': [],
            'context': dict(context, active_ids=wizard_data_ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': wizard_data_ids[0] or False,
        }

    def wizard_cancel(self, cursor, uid, ids, context):
        '''
        Cancel the export: just drop the file
        '''

        wizard_data = self.browse(cursor, uid, ids, context)[0]
        result_model = self.pool.get('banking.export.hsbc')

        try:
            result_model.unlink(cursor, uid, wizard_data.file_id.id)
        except AttributeError:
            # file_id missing, wizard storage gone, server was restarted
            pass

        return {'type': 'ir.actions.act_window_close'}

    def wizard_save(self, cursor, uid, ids, context):
        '''
        Save the export: mark all payments in the file as 'sent'
        '''

        wizard_data = self.browse(cursor, uid, ids, context)[0]
        result_model = self.pool.get('banking.export.hsbc')
        po_model = self.pool.get('payment.order')

        result_model.write(cursor, uid, [wizard_data.file_id.id],
                           {'state': 'sent'})

        po_ids = [po.id for po in wizard_data.payment_order_ids]
        po_model.action_sent(cursor, uid, po_ids)

        return {'type': 'ir.actions.act_window_close'}
