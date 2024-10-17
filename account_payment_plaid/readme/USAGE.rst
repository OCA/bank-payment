Using the Plaid API for bank transfers on production or development environment:

#. Go to "Settings" > "Plaid".
#. Add your Plaid credentials.
#. Synchronize with Plaid.
#. Select your bank account.
#. Go to "Contacts" and add the plaid client id for the contact.
#. Go to your invoice and click on "Pay with Plaid" button.\nYou can see the button if the bill is confirmed.\nWhen you click on the button, you will see a confirmation window.
#. When you confirm the payment and the confirmation window\nis closed you can see the transfer in "Settings" > "Technical" > "Plaid" > "Transfer".
#. When the transfer is done, you can see the bill as paid and the payment create on odoo.

If you are using the sandbox environment for testing,
do you need to use the simulation method for simulate the transfer.
This method only works with the sandbox environment.
You can found this method on "Settings" > "Technical" > "Plaid" > "Transfer".

#.  Select the transfer that you want to simulate.
#.  Click on "Simulate Transfer" button.
#.  Select the command that you want to simulate.
    * "Simulate Transfer" : This command create a event on sandbox environment.\nDo you need this event for check the status of the transfer on Odoo.
    * "Simulate transfer ledger available" : This command simulate converting pending balance\nto available balance for all originators in the Sandbox environment.
#. Click on "Confirm" button.

This addon use the cron for check the status of the transfer on Plaid and update the bill and payment.
If you need more information about Plaid, please visit the `Plaid website <https://plaid.com>`_ or `Plaid Docs Transfer <https://plaid.com/docs/transfer/>`_.
