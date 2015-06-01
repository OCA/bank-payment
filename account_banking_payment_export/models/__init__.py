# -*- coding: utf-8 -*-
from . import account_payment
# important: import payment_mode_type before payment_mode
# to let the _auto_init work properly
from . import payment_mode_type
from . import payment_mode
from . import account_move_line
from . import account_invoice
