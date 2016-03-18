# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Compassion CH (<http://www.compassion.ch>)
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
"""
This script covers the migration of the 0.1 to 0.2 version of sepa mandates.
As table names changed, we want to migrate values from sdd_mandate table to
newly created account_banking_mandate. We also copy foreign keys in invoice
and payment lines.
Finally, we remove useless fields (sdd_mandate_id) and obsolete table
(sdd_mandate).
"""

__name__ = "account.banking.sepa.direct_debit:: Move sdd_mandate data to " \
           "account_banking_mandate"


def migrate(cr, installed_version):
    if not installed_version:
        return

    def table_exists(cr, table):
        cr.execute(
            "SELECT 1 FROM information_schema.tables"
            " WHERE table_name='%s' LIMIT 1;" % table
        )
        return cr.fetchall() and True or False

    if table_exists(cr, 'sdd_mandate'):
        query = (
            "INSERT INTO account_banking_mandate "
            "(id, create_uid, create_date, write_date, write_uid, "
            "partner_bank_id, last_debit_date, scan, company_id, state, "
            "unique_mandate_reference, signature_date, sepa_migrated, "
            "original_mandate_identification, recurrent_sequence_type, type, "
            "scheme) "
            "SELECT id, create_uid, create_date, write_date, write_uid, "
            "partner_bank_id, last_debit_date, scan, company_id, state, "
            "unique_mandate_reference, signature_date, sepa_migrated, "
            "original_mandate_identification, recurrent_sequence_type, type, "
            "'CORE' "
            "FROM sdd_mandate"
        )
        cr.execute(query)
        query2 = "UPDATE account_invoice SET mandate_id=sdd_mandate_id"
        cr.execute(query2)
        query3 = "UPDATE payment_line SET mandate_id=sdd_mandate_id"
        cr.execute(query3)
        query4 = \
            "ALTER TABLE account_invoice DROP COLUMN IF EXISTS sdd_mandate_id"
        cr.execute(query4)
        query5 = \
            "ALTER TABLE payment_line DROP COLUMN IF EXISTS sdd_mandate_id"
        cr.execute(query5)
        query6 = "DROP TABLE IF EXISTS sdd_mandate CASCADE"
        cr.execute(query6)
