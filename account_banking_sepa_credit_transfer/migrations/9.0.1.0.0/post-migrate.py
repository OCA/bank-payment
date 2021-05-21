# coding: utf-8
# Copyright 2018 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, SUPERUSER_ID


def migrate(cr, version):
    """ Switch code and version around on noupdate data """
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    for method in env['account.payment.method'].search([
            ('code', '=like', 'pain.001%')]):
        method.write({
            'bank_account_required': True,
            'code': 'sepa_credit_transfer',
            'pain_version': method.code,
            'payment_type': 'outbound',
        })
