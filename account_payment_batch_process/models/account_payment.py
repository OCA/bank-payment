# -*- coding: utf-8 -*-
# Copyright 2017 Ursa Information Systems <http://www.ursainfosystems.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment
            references invoice(s) they are reconciled.
            Return the journal entry.
        """
        # If group data
        if 'group_data' in self._context:
            aml_obj = self.env['account.move.line'].\
                with_context(check_move_validity=False)
            invoice_currency = False
            if self.invoice_ids and\
                    all([x.currency_id == self.invoice_ids[0].currency_id
                         for x in self.invoice_ids]):
                # If all the invoices selected share the same currency,
                # record the paiement in that currency too
                invoice_currency = self.invoice_ids[0].currency_id
            move = self.env['account.move'].create(self._get_move_vals())
            p_id = str(self.partner_id.id)
            for inv in self._context.get('group_data')[p_id]['inv_val']:
                amt = 0
                if 'is_customer' in self._context and\
                        self._context.get('is_customer'):
                    amt = -(self._context.get('group_data')[p_id]['inv_val']
                            [inv]['receiving_amt'])
                else:
                    amt = self._context.get('group_data')[p_id]['inv_val'][inv]

                debit, credit, amount_currency, currency_id =\
                    aml_obj.with_context(date=self.payment_date).\
                    compute_amount_fields(amt, self.currency_id,
                                          self.company_id.currency_id,
                                          invoice_currency)
                # Write line corresponding to invoice payment
                counterpart_aml_dict =\
                    self._get_shared_move_line_vals(debit,
                                                    credit, amount_currency,
                                                    move.id, False)
                current_invoice = self.env['account.invoice'].browse(int(inv))
                counterpart_aml_dict.update(
                    self._get_counterpart_move_line_vals(current_invoice))
                counterpart_aml_dict.update({'currency_id': currency_id})
                counterpart_aml = aml_obj.create(counterpart_aml_dict)
                # Reconcile with the invoices and write off
                if 'is_customer' in self._context and\
                        self._context.get('is_customer'):
                    handling = self._context.get('group_data')[p_id]['inv_val'][inv]['handling']  # noqa
                    payment_difference = self._context.get('group_data')[p_id]['inv_val'][inv]['payment_difference']  # noqa
                    writeoff_account_id = self._context.get('group_data')[p_id]['inv_val'][inv]['writeoff_account_id']  # noqa
                    if handling == 'reconcile' and\
                            payment_difference:
                        writeoff_line =\
                            self._get_shared_move_line_vals(0, 0, 0, move.id,
                                                            False)
                        debit_wo, credit_wo, amount_currency_wo, currency_id =\
                            aml_obj.with_context(date=self.payment_date).\
                            compute_amount_fields(
                                payment_difference,
                                self.currency_id,
                                self.company_id.currency_id,
                                invoice_currency)
                        writeoff_line['name'] = _('Counterpart')
                        writeoff_line['account_id'] = writeoff_account_id
                        writeoff_line['debit'] = debit_wo
                        writeoff_line['credit'] = credit_wo
                        writeoff_line['amount_currency'] = amount_currency_wo
                        writeoff_line['currency_id'] = currency_id
                        writeoff_line = aml_obj.create(writeoff_line)
                        if counterpart_aml['debit']:
                            counterpart_aml['debit'] += credit_wo - debit_wo
                        if counterpart_aml['credit']:
                            counterpart_aml['credit'] += debit_wo - credit_wo
                        counterpart_aml['amount_currency'] -=\
                            amount_currency_wo
                current_invoice.register_payment(counterpart_aml)
                # Write counterpart lines
                if not self.currency_id != self.company_id.currency_id:
                    amount_currency = 0
                liquidity_aml_dict =\
                    self._get_shared_move_line_vals(credit, debit,
                                                    -amount_currency, move.id,
                                                    False)
                liquidity_aml_dict.update(
                    self._get_liquidity_move_line_vals(-amount))
                aml_obj.create(liquidity_aml_dict)
            move.post()
            return move

        return super(AccountPayment, self)._create_payment_entry(amount)
