# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    if not version:
        return

    cr.execute('ALTER TABLE res_partner_bank DROP COLUMN IF EXISTS acc_type')
