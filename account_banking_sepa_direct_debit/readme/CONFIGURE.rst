For setting the SEPA creditor identifier:

#. Go to Invoicing/Accounting > Configuration > Settings.
#. On the field "SEPA Creditor Identifier" in the section *SEPA/PAIN*, you can
   fill the corresponding identifier.

If your country requires several identifiers (like Spain), you must:

#. Go to *Invoicing/Accounting > Configuration > Settings*.
#. On the section *SEPA/PAIN*, check the mark "Multiple identifiers".
#. Now go to *Invoicing/Accounting > Configuration > Management > Payment Modes*.
#. Create a payment mode for your specific bank.
#. Fill the specific identifier on the field "SEPA Creditor Identifier".

For defining a payment mode that uses SEPA direct debit:

#. Go to *Invoicing/Accounting > Configuration > Management > Payment Modes*.
#. Create a record.
#. Select the Payment Method *SEPA Direct Debit for customers* (which is
   automatically created upon module installation).
#. Check that this payment method uses the proper version of PAIN.
#. If not, go *Invoicing/Accounting > Configuration > Management > Payment Methods*.
#. Locate the "SEPA Direct Debit for customers" record and open it.
#. Change the "PAIN version" according your needs.
#. If you need to handle several PAIN versions, just duplicate the payment
   method adjusting this field on each for having them.
