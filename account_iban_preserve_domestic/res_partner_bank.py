from osv import fields,osv
class res_partner_bank(osv.osv):
    ''' Adds a field for domestic account numbers '''
    _inherit = "res.partner.bank"

    _columns = {
        'acc_number_domestic': fields.char(
            'Domestic Account Number', size=64)
        }

res_partner_bank()

