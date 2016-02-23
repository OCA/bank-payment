# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos <omar@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class BankingExportPain(models.AbstractModel):
    _inherit = 'banking.export.pain'

    @api.model
    def generate_initiating_party_block(self, parent_node, gen_args):
        res = super(BankingExportPain, self).\
            generate_initiating_party_block(parent_node, gen_args)

        if self.payment_order_ids[0].mode.suffix:
            other_id_code = parent_node.xpath('//InitgPty/Id/OrgId/Othr/Id')
            if other_id_code:
                initiating_party_identifier =\
                    self.payment_order_ids[0].company_id.\
                    initiating_party_identifier
                other_id_code[0].text = initiating_party_identifier[:-3] + \
                    self.payment_order_ids[0].mode.suffix

        return res

    @api.model
    def generate_creditor_scheme_identification(
            self, parent_node, identification, identification_label,
            eval_ctx, scheme_name_proprietary, gen_args):

        res = super(BankingExportPain, self).\
            generate_creditor_scheme_identification(parent_node,
                                                    identification,
                                                    identification_label,
                                                    eval_ctx,
                                                    scheme_name_proprietary,
                                                    gen_args)
        if self.payment_order_ids[0].mode.suffix:
            other_id_code = parent_node.\
                xpath('//PrvtId/Othr/Id')
            if other_id_code:
                sepa_creditor_identifier = self.\
                    _prepare_field(identification_label, identification,
                                   eval_ctx, gen_args=gen_args)
                other_id_code[0].text = sepa_creditor_identifier[:4] + \
                    self.payment_order_ids[0].mode.suffix + \
                    sepa_creditor_identifier[7:]

        return res
