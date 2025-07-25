# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


def post_init_hook(env):
    fields_mapping = [
        ("property_account_receivable_id", "property_stored_account_receivable_id"),
        ("property_account_payable_id", "property_stored_account_payable_id"),
    ]
    for company in env["res.company"].search([]):
        partners = (
            env["res.partner"]
            .with_company(company.id)
            .with_context(active_test=False)
            .search([])
        )
        for partner in partners:
            vals = {}
            for orig, dest in fields_mapping:
                if partner[orig] and not partner[dest]:
                    vals[dest] = partner[orig].id
            if vals:
                partner.with_company(company.id).write(vals)


def uninstall_hook(env):
    fields_mapping = [
        ("property_account_receivable_id", "property_stored_account_receivable_id"),
        ("property_account_payable_id", "property_stored_account_payable_id"),
    ]
    for company in env["res.company"].search([]):
        partners = (
            env["res.partner"]
            .with_company(company.id)
            .with_context(active_test=False)
            .search([])
        )
        for partner in partners:
            vals = {}
            for orig, dest in fields_mapping:
                if not partner[orig] and partner[dest]:
                    vals[orig] = partner[dest].id
            if vals:
                partner.with_company(company.id).write(vals)
