=============
IPpay Payment
=============

This module allows to register payments using IPpay.

Usage
=====
Install the module. Activate payment acquirer named IPpay.Configure journal for it and allow it to make electronic payments. Add API URL and API TerminalId in Ippay config. Then add a credit card for a partner. Create an invoice for related customers and Make payment using IPpay Payment journal.
In Batch Payment using a credit card, a payment confirmation will done through cron job named 'Post process payment transactions'. 

Credits
=======

* Open Source Integrators <http://www.opensourceintegrators.com>
* Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>

Contributors
------------

* Maxime Chambreuil <mchambreuil@opensourceintegrators.com>
* Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>
