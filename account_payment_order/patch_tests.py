# Copyright 2025 Simone Rubino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""
Some test classes inheriting from AccountTestInvoicingCommon
assume that the default users can create `res.partner.bank` records.
One example is the core module `l10n_it_edi`
in https://github.com/odoo/odoo/blob/
b1a91bac849871ec37510fa97747285fe373bd22/addons/l10n_it_edi/tests/common.py#L59.
Due to Odoo's modular architecture, these test classes' module
might not even have `account_payment_order` in their dependencies.

With this patch, default users in
test classes inheriting from AccountTestInvoicingCommon
are able to create `res.partner.bank` records.
"""

from odoo.tools import config

if config["test_enable"] or config["test_file"]:
    from odoo.addons.account.tests.common import AccountTestInvoicingCommon

    original_get_default_groups = AccountTestInvoicingCommon.get_default_groups

    @classmethod
    def patched_default_groups(cls):
        groups = original_get_default_groups.__func__(cls)
        if new_group := cls.env.ref(
            "account_payment_order.group_account_payment",
            raise_if_not_found=False,
        ):
            groups |= new_group
        return groups

    AccountTestInvoicingCommon.get_default_groups = patched_default_groups
