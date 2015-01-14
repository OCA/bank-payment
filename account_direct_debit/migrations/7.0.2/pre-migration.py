# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Therp BV (<http://therp.nl>).
#
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
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

import logging
logger = logging.getLogger()


def rename_columns(cr, column_spec):
    """
    Rename table columns. Taken from OpenUpgrade.

    :param column_spec: a hash with table keys, with lists of tuples as \
    values. Tuples consist of (old_name, new_name).

    """
    for table in column_spec.keys():
        for (old, new) in column_spec[table]:
            logger.info("table %s, column %s: renaming to %s", table, old, new)
            cr.execute('ALTER TABLE %s RENAME %s TO %s' % (table, old, new,))
            cr.execute('DROP INDEX IF EXISTS "%s_%s_index"' % (table, old))


def migrate(cr, version):
    if not version:
        return

    # rename field debit_move_line_id
    rename_columns(cr, {
        'payment_line': [
            ('debit_move_line_id', 'banking_addons_61_debit_move_line_id'),
        ]
    })
