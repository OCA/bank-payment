# -*- encoding: utf-8 -*-
##############################################################################
#
#  Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#  All Rights Reserved
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from tools.translate import _

class mem_bank_statement(object):
    '''
    A mem_bank_statement is a real life projection of a bank statement paper
    containing a report of one or more transactions done. As these reports can
    contain payments that originate in several accounting periods, period is an
    attribute of mem_bank_transaction, not of mem_bank_statement.
    Also note that the statement_id is copied from the bank statement, and not
    generated from any sequence. This enables us to skip old data in new
    statement files.
    '''
    # Lock attributes to enable parsers to trigger non-conformity faults
    __slots__ = [
        'start_balance','end_balance', 'date', 'local_account',
        'local_currency', 'id', 'statements'
    ]
    def __init__(self, *args, **kwargs):
        super(mem_bank_statement, self).__init__(*args, **kwargs)
        self.id = ''
        self.local_account = ''
        self.local_currency = ''
        self.start_balance = 0.0
        self.end_balance = 0.0
        self.date = ''
        self.transactions = []

    def is_valid(self):
        '''
        Final check: ok if calculated end_balance and parsed end_balance are
        identical and perform a heuristic check on the transactions.
        '''
        if any([x for x in self.transactions if not x.is_valid()]):
            return False
        check = float(self.start_balance)
        for transaction in self.transactions:
            check += float(transaction.transferred_amount)
        return abs(check - float(self.end_balance)) < 0.0001

class mem_bank_transaction(object):
    '''
    A mem_bank_transaction is a real life copy of a bank transfer. Mapping to
    OpenERP moves and linking to invoices and the like is done afterwards.
    '''
    # Lock attributes to enable parsers to trigger non-conformity faults
    __slots__ = [
        'id', 'local_account', 'local_currency', 'execution_date',
        'effective_date', 'remote_owner', 'remote_account',
        'remote_currency', 'transferred_amount', 'transfer_type',
        'reference', 'message', 'statement_id',
    ]

    # transfer_type's to be used by the business logic.
    # Depending on the type your parser gives a transaction, different
    # behavior can be triggered in the business logic.
    #
    #   BANK_COSTS          Automated credited costs by the bank.
    #                       Used to generate an automated invoice from the bank
    #                       Will be excluded from matching.
    #   BANK_TERMINAL       A cash withdrawal from a bank terminal.
    #                       Will be excluded from matching.
    #   CHECK               A delayed payment. Can be used to trigger extra
    #                       moves from temporary accounts. (Money away).
    #                       TODO: No special treatment yet.
    #                       Will be selected for matching.
    #   DIRECT_DEBIT        Speaks for itself. When outgoing (credit) and
    #                       matched, can signal the matched invoice triaged.
    #                       Will be selected for matching.
    #   ORDER               Order to the bank. Can work both ways.
    #                       Will be selected for matching.
    #   PAYMENT_BATCH       A payment batch. Can work in both directions.
    #                       Incoming payment batch transactions can't be
    #                       matched with payments, outgoing can.
    #                       Will be selected for matching.
    #   PAYMENT_TERMINAL    A payment with debit/credit card in a (web)shop
    #                       Invoice numbers and other hard criteria are most
    #                       likely missing.
    #                       Will be selected for matching
    #   PERIODIC_ORDER      An automated payment by the bank on your behalf.
    #                       Always outgoing.
    #                       Will be selected for matching.
    #
    #   Perhaps more will follow.
    #
    # When writing parsers, map other types with similar meaning to these to
    # prevent cluttering the API. For example: the Dutch ING Bank has a
    # transfer type Post Office, meaning a cash withdrawal from one of their
    # agencies. This can be mapped to BANK_TERMINAL without losing any
    # significance for OpenERP.

    BANK_COSTS = 'BC'
    BANK_TERMINAL = 'BT'
    CHECK = 'CK'
    DIRECT_DEBIT = 'DD'
    ORDER = 'DO'
    PAYMENT_BATCH = 'PB'
    PAYMENT_TERMINAL = 'PT' 
    PERIODIC_ORDER = 'PO'

    types = [
        BANK_COSTS, BANK_TERMINAL, CHECK, DIRECT_DEBIT, ORDER,
        PAYMENT_BATCH, PAYMENT_TERMINAL, PERIODIC_ORDER,
    ]
    type_map = {
        # This can be a translation map of type versus bank type. Each key is
        # the real transfer_type, each value is the mem_bank_transaction.type
    }

    def __init__(self, *args, **kwargs):
        super(mem_bank_transaction, self).__init__(*args, **kwargs)
        self.id = ''
        self.local_account = ''
        self.local_currency = ''
        self.execution_date = ''
        self.effective_date = ''
        self.remote_account = ''
        self.remote_owner = ''
        self.remote_currency = ''
        self.transferred_amount = ''
        self.transfer_type = ''
        self.reference = ''
        self.message = ''
        self.statement_id = ''

    def copy(self):
        '''
        Return a copy of self
        '''
        retval = mem_bank_transaction()
        for attr in self.__slots__:
            setattr(retval, attr, getattr(self, attr))
        return retval

    def _get_type(self):
        if self.transfer_type in self.type_map:
            return self.type_map[self.transfer_type]
        return self.transfer_type

    def _set_type(self, value):
        if value in self.types:
            self.transfer_type = value
        else:
            raise ValueError, _('Invalid value for transfer_type')

    type = property(_get_type, _set_type)

    def is_valid(self):
        '''
        Heuristic check: at least id, execution_date, remote_account and
        transferred_amount should be filled to create a valid transfer.
        '''
        return (self.execution_date and self.remote_account
                and self.transferred_amount and True) or False

class parser_type(type):
    '''
    Meta annex factory class for house keeping and collecting parsers.
    '''
    parsers = []
    parser_by_name = {}
    parser_by_code = {}
    parser_by_classname = {}

    def __new__(metacls, clsname, bases, clsdict):
        newcls = type.__new__(metacls, clsname, bases, clsdict)
        if 'name' in clsdict and newcls.name:
            metacls.parsers.append(newcls)
            metacls.parser_by_name[newcls.name] = newcls
            metacls.parser_by_code[newcls.code] = newcls
            metacls.parser_by_classname[clsname] = newcls
        return newcls

    @classmethod
    def get_parser_types(cls, sort='name'):
        '''
        Return the parser class names, optional in sort order.
        '''
        if sort == 'name':
            keys = cls.parser_by_name.keys()
            parsers = cls.parser_by_name
        else:
            keys = cls.parser_by_code.itervalues()
            parsers = cls.parser_by_code
        keys.sort()
        return [(parsers[x].code, parsers[x].name) for x in keys]

def create_parser(code):
    if code in parser_type.parser_by_code:
        return parser_type.parser_by_code[code]()
    return None

class parser(object):
    '''
    A parser delivers the interface for any parser object. Inherit from
    it to implement your own.
    You should at least implement the following at the class level:
        name -> the name of the parser, shown to the user and
                    translatable.
        code -> the identifier you care to give it. Not translatable
        doc  -> the description of the identifier. Shown to the user.
                    Translatable.

        parse -> the method for the actual parsing.
    '''
    __metaclass__ = parser_type
    name = None
    code = None
    doc = __doc__

    def parse(self, data):
        '''
        Parse data.
        
        data is a raw in memory file object. You have to split it in
        whatever chunks you see fit for parsing. It should return a list
        of mem_bank_statement objects. Every mem_bank_statement object
        should contain a list of mem_bank_transaction objects.

        For identification purposes, don't invent numbering of the transaction
        numbers or bank statements ids on your own - stick with those provided
        by your bank. Doing so enables the users to re-load old transaction
        files without creating multiple identical bank statements.
        '''
        raise NotImplementedError(
            _('This is a stub. Please implement your own.')
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
