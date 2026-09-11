from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute(
        """
        UPDATE res_partner_bank bank
           SET allow_out_payment = TRUE
          FROM account_payment payment
         WHERE payment.partner_bank_id = bank.id
           AND payment.payment_type = 'outbound'
           AND payment.payment_order_id IS NOT NULL
        """
    )
