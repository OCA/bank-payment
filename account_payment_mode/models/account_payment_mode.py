# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPaymentMode(models.Model):
    """This corresponds to the object payment.mode of v8 with some
    important changes. It also replaces the object payment.method
    of the module sale_payment_method of OCA/e-commerce"""
    _name = "account.payment.mode"
    _description = 'Payment Modes'
    _order = 'name'

    name = fields.Char(string='Name', required=True, translate=True)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, ondelete='restrict',
        default=lambda self: self.env['res.company']._company_default_get(
            'account.payment.mode'))
    bank_account_link = fields.Selection([
        ('fixed', 'Fixed'),
        ('variable', 'Variable'),
        ], string='Link to Bank Account', required=True,
        help="For payment modes that are always attached to the same bank "
        "account of your company (such as wire transfer from customers or "
        "SEPA direct debit from suppliers), select "
        "'Fixed'. For payment modes that are not always attached to the same "
        "bank account (such as SEPA Direct debit for customers, wire transfer "
        "to suppliers), you should choose 'Variable', which means that you "
        "will select the bank account on the payment order. If your company "
        "only has one bank account, you should always select 'Fixed'.")
    fixed_journal_id = fields.Many2one(
        'account.journal', string='Fixed Bank Journal',
        domain=[('type', '=', 'bank')], ondelete='restrict')
    # I need to use the old definition, because I have 2 M2M fields
    # pointing to account.journal
    variable_journal_ids = fields.Many2many(
        'account.journal',
        'account_payment_mode_variable_journal_rel',
        'payment_mode_id', 'journal_id',
        string='Allowed Bank Journals',
        domain=[('type', '=', 'bank')])
    payment_method_id = fields.Many2one(
        'account.payment.method', string='Payment Method', required=True,
        ondelete='restrict')  # equivalent v8 field : type
    payment_type = fields.Selection(
        related='payment_method_id.payment_type', readonly=True, store=True,
        string="Payment Type")
    payment_method_code = fields.Char(
        related='payment_method_id.code', readonly=True, store=True,
        string='Payment Method Code')
    active = fields.Boolean(string='Active', default=True)
    # I dropped sale_ok and purchase_ok fields, because it is replaced by
    # payment_type = 'inbound' or 'outbound'
    # In fact, with the new v9 datamodel, you MUST create 2 payment modes
    # for wire transfer : one for wire transfer from your customers (inbound)
    # and one for wire transfer to your suppliers (outbound)
    note = fields.Text(string="Note", translate=True)

    @api.multi
    @api.constrains(
        'bank_account_link', 'fixed_journal_id', 'payment_method_id')
    def bank_account_link_constrains(self):
        for mode in self:
            if mode.bank_account_link == 'fixed':
                if not mode.fixed_journal_id:
                    raise ValidationError(_(
                        "On the payment mode '%s', the bank account link is "
                        "'Fixed' but the fixed bank journal is not set")
                        % mode.name)
                else:
                    if mode.payment_method_id.payment_type == 'outbound':
                        if (
                                mode.payment_method_id.id not in
                                mode.fixed_journal_id.
                                outbound_payment_method_ids.ids):
                            raise ValidationError(_(
                                "On the payment mode '%s', the payment method "
                                "is '%s', but this payment method is not part "
                                "of the payment methods of the fixed bank "
                                "journal '%s'") % (
                                    mode.name,
                                    mode.payment_method_id.name,
                                    mode.fixed_journal_id.name))
                    else:
                        if (
                                mode.payment_method_id.id not in
                                mode.fixed_journal_id.
                                inbound_payment_method_ids.ids):
                            raise ValidationError(_(
                                "On the payment mode '%s', the payment method "
                                "is '%s' (it is in fact a debit method), "
                                "but this debit method is not part "
                                "of the debit methods of the fixed bank "
                                "journal '%s'") % (
                                    mode.name,
                                    mode.payment_method_id.name,
                                    mode.fixed_journal_id.name))
