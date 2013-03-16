from openerp.osv import orm, fields


class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'
    _columns = {
        'match_type': fields.related(
            # Add payment and storno types
            'import_transaction_id', 'match_type', type='selection',
            selection=[('manual', 'Manual'), ('move','Move'),
                       ('invoice', 'Invoice'), ('payment', 'Payment'),
                       ('payment_order', 'Payment order'),
                       ('storno', 'Storno')], 
            string='Match type', readonly=True,),
        }
