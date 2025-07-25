from odoo import fields


def monkey_patch(cls):
    """Based on the Odoo module "base_sparse_field"."""

    def decorate(func):
        name = func.__name__
        func.super = getattr(cls, name, None)
        setattr(cls, name, func)
        return func

    return decorate


@monkey_patch(fields.Field)
def get_company_dependent_fallback(self, records):
    """
    Necessary because Odoo, in module "account", tests that the
    field "property_account_receivable_id" is company dependent
    """
    if self.name in ["property_account_receivable_id", "property_account_payable_id"]:
        return records[self.name]
    return get_company_dependent_fallback.super(self, records)
