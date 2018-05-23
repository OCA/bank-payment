# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    """ for done statements, set date_done if not set from date_scheduled """
    cr.execute(
        'update payment_order '
        'set date_done=coalesce(date_scheduled, write_date) '
        "where state='done' and date_done is null"
    )
