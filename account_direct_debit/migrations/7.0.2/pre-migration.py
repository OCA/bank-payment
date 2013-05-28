def migrate(cr, version):
    if not version:
        return
    # workflow state moved to another module
    cr.execute(
        """
        UPDATE ir_model_data 
        SET module = 'account_banking_payment'
        WHERE name = 'trans_done_sent'
        AND module = 'account_direct_debit'
        """)
        
