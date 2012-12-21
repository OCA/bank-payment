from osv import fields,osv
class res_partner_bank(osv.osv):
    '''Bank Accounts'''
    _inherit = "res.partner.bank"

    def _get_domestic(self, cr, uid, ids, prop, unknow_none, context=None):
        res = dict(
            [(x['id'], x['acc_number'])
             for x in self.read(cr, uid, ids, ['acc_number'], context=context)
             ]
            )
        return res

    _columns = {
        'acc_number_domestic': fields.function(
            _get_domestic, method=True, type="char",
            size=64, string='Domestic Account Number',
            store = {
                'res.partner.bank':(
                    lambda self,cr,uid,ids,c={}:ids, 
                    ['acc_number'], 10),
                },
            ),
        }

res_partner_bank()

