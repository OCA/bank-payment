# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    for order in env['account.payment.order'].search([
            ('state', '=', 'uploaded'),
    ]):
        if order._all_lines_reconciled():
            order.action_done()
