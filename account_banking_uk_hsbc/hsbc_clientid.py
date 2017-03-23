# -*- coding: utf-8 -*-
from openerp.osv import orm, fields


class hsbc_clientid(orm.Model):
    """
    Record to hold the HSBCNet Client ID for the company.
    """
    _name = 'banking.hsbc.clientid'
    _description = 'HSBC Client ID'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'clientid': fields.char('Client ID', size=20, required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }

    _defaults = {
        'company_id': (
            lambda self, cr, uid, c:
            self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id),
    }


class payment_order(orm.Model):
    _inherit = 'payment.order'
    _columns = {
        'hsbc_clientid_id': fields.many2one(
            'banking.hsbc.clientid',
            'HSBC Client ID',
            required=True,
        ),
    }

    def _default_hsbc_clientid(self, cr, uid, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company_id = user.company_id.id

        clientid_ids = self.pool['banking.hsbc.clientid'].search(
            cr, uid, [('company_id', '=', company_id)]
        )
        if len(clientid_ids) == 0:
            return False
        else:
            return clientid_ids[0]

    _defaults = {
        'hsbc_clientid_id': _default_hsbc_clientid,
    }
