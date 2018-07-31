# Copyright 2018 Brain-Tec Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def set_account_holder(cr):
    cr.execute("""
        UPDATE res_partner_bank SET account_holder =
        (SELECT name FROM res_partner WHERE res_partner.id =
        res_partner_bank.partner_id)
        """)
    cr.commit()


def migrate(cr, version):
    set_account_holder(cr)
