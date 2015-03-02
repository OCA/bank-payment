# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Therp BV (<http://therp.nl>).
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

{
    'name': 'IBAN - Bic not required',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': "Banking addons community,Odoo Community Association (OCA)",
    'website': 'https://launchpad.net/banking-addons',
    'category': 'Banking addons',
    'depends': [
        'base_iban',
    ],
    'description': '''
The account_iban module in OpenERP mandates the presence of a BIC
code on an IBAN account number through a constraint. However, as of
Februari 2012 there is a resolution from the EU that drops this requirement
(see section 8 of [1]). This module reverts the constraint on BICs in the
base_iban module.

See also https://bugs.launchpad.net/openobject-addons/+bug/933472

[1] http://goo.gl/iXM2Cg
    ''',
    'data': [
        'data/res_partner_bank_type_field.xml',
    ],
    'installable': True,
}
