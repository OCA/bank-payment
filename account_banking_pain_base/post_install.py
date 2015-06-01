# -*- encoding: utf-8 -*-
##############################################################################
#
#    PAIN Base module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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


def set_default_initiating_party(cr, registry):
    party_issuer_per_country = {
        'BE': 'KBO-BCE',  # KBO-BCE = the registry of companies in Belgium
    }
    cr.execute('''
        SELECT
            res_company.id,
            res_country.code AS country_code,
            res_partner.vat,
            res_company.initiating_party_identifier,
            res_company.initiating_party_issuer
        FROM res_company
        LEFT JOIN res_partner ON res_partner.id = res_company.partner_id
        LEFT JOIN res_country ON res_country.id = res_partner.country_id
        ''')
    for company in cr.dictfetchall():
        country_code = company['country_code']
        if not company['initiating_party_issuer']:
            if country_code and country_code in party_issuer_per_country:
                cr.execute(
                    'UPDATE res_company SET initiating_party_issuer=%s '
                    'WHERE id=%s',
                    (party_issuer_per_country[country_code], company['id']))
        party_identifier = False
        if not company['initiating_party_identifier']:
            if company['vat'] and country_code:
                if country_code == 'BE':
                    party_identifier = company['vat'][2:].replace(' ', '')
            if party_identifier:
                cr.execute(
                    'UPDATE res_company SET initiating_party_identifier=%s '
                    'WHERE id=%s',
                    (party_identifier, company['id']))
    return
