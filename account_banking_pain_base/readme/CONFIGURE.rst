#. Go to Invoicing/Accounting > Configuration > Settings.
#. On the fields "Initiating Party Issuer" and "Initiating Party Identifier",
   in the section *SEPA/PAIN*, you can fill the corresponding identifiers.

If your country requires several identifiers (like Spain), you must:

#. Go to *Invoicing/Accounting > Configuration > Settings*.
#. On the section *SEPA/PAIN*, check the mark "Multiple identifiers".
#. Now go to *Invoicing/Accounting > Configuration > Management > Payment Modes*.
#. Create a payment mode for your specific bank.
#. Fill the specific identifiers on the fields "Initiating Party Identifier"
   and "Initiating Party Issuer".

#. When configuring a SEPA Credit Transfer payment method, you can choose the
   PAIN format version to use.

   Starting from this version, **PAIN.001.001.09** is available and is
   *recommended for credit transfers*, as it complies with the newer EPC
   requirements regarding postal address structure.

   During upgrade, existing **SEPA Credit Transfer** payment methods that still
   use an older **pain.001.001.03** format are **migrated automatically** to
   **PAIN.001.001.09** to avoid generating files that may be rejected by banks.
   You can still change the PAIN version afterwards if your bank requires a
   different one.
