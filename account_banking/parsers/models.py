# coding: utf-8
##############################################################################
#
#  Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#  All Rights Reserved
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import re
from difflib import SequenceMatcher
from openerp.tools.translate import _


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
        'start_balance',
        'end_balance',
        'date',
        'local_account',
        'local_currency',
        'id',
        'transactions'
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

        'id',
        # Message id

        'statement_id',
        # The bank statement this message was reported on

        'transfer_type',
        # Action type that initiated this message

        'reference',
        # A reference to this message for communication

        'local_account',
        # The account this message was meant for

        'local_currency',
        # The currency the bank used to process the transferred amount

        'execution_date',
        # The posted date of the action

        'value_date',
        # The value date of the action

        'remote_account',
        # The account of the other party

        'remote_currency',
        # The currency used by the other party

        'exchange_rate',
        # The exchange rate used for conversion of local_currency and
        # remote_currency

        'transferred_amount',
        # The actual amount transferred -
        #   negative means sent, positive means received
        # Most banks use the local_currency to express this amount, but there
        # may be exceptions I'm unaware of.

        'message',
        # A direct message from the initiating party to the receiving party
        #   A lot of banks abuse this to stuff all kinds of structured
        #   information in this message. It is the task of the parser to split
        #   this up into the appropriate attributes.

        'remote_owner',
        # The name of the other party

        'remote_owner_address',
        # The other parties address lines - the only attribute that is a list

        'remote_owner_city',
        # The other parties city name belonging to the previous

        'remote_owner_postalcode',
        # The other parties postal code belonging to the address

        'remote_owner_country_code',
        # The other parties two letter ISO country code belonging to the
        # previous

        'remote_owner_custno',
        # The other parties customer number

        # For identification of private other parties, the following attributes
        # are available and self explaining. Most banks allow only one per
        # message.
        'remote_owner_ssn',
        'remote_owner_tax_id',
        'remote_owner_employer_id',
        'remote_owner_passport_no',
        'remote_owner_idcard_no',
        'remote_owner_driverslicense_no',

        # Other private party information fields. Not all banks use it, but
        # at least SEPA messaging allowes it.
        'remote_owner_birthdate',
        'remote_owner_cityofbirth',
        'remote_owner_countryofbirth',
        'remote_owner_provinceofbirth',

        # For the identification of remote banks, the following attributes are
        # available and self explaining. Most banks allow only one per
        # message.
        'remote_bank_bic',
        'remote_bank_bei',
        'remote_bank_ibei',
        'remote_bank_eangln',
        'remote_bank_chips_uid',
        'remote_bank_duns',
        'remote_bank_tax_id',

        # For other identification purposes: both of the next attributes must
        # be filled.
        'remote_bank_proprietary_id',
        'remote_bank_proprietary_id_issuer',

        # The following attributes are for allowing banks to communicate about
        # specific transactions. The transferred_amount must include these
        # costs.
        # Please make sure that the costs are signed for the right direction.
        'provision_costs',
        'provision_costs_currency',
        'provision_costs_description',

        # An error message for interaction with the user
        # Only used when mem_transaction.valid returns False.
        'error_message',

        # Storno attribute. When True, make the cancelled debit eligible for
        # a next direct debit run
        'storno_retry',

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
    #   STORNO              A failed or reversed attempt at direct debit.
    #                       Either due to an action on the payer's side
    #                       or a failure observed by the bank (lack of
    #                       credit for instance)
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
    STORNO = 'ST'

    types = [
        BANK_COSTS, BANK_TERMINAL, CHECK, DIRECT_DEBIT, ORDER,
        PAYMENT_BATCH, PAYMENT_TERMINAL, PERIODIC_ORDER, STORNO,
    ]
    type_map = {
        # This can be a translation map of type versus bank type. Each key is
        # the real transfer_type, each value is the mem_bank_transaction.type
    }

    def __init__(self, *args, **kwargs):
        '''
        Initialize values
        '''
        super(mem_bank_transaction, self).__init__(*args, **kwargs)
        for attr in self.__slots__:
            setattr(self, attr, '')
        self.remote_owner_address = []

    def copy(self):  # noqa: W8106
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
            raise ValueError(_('Invalid value for transfer_type'))

    type = property(_get_type, _set_type)

    def is_valid(self):
        '''
        Heuristic check: at least id, execution_date, remote_account and
        transferred_amount should be filled to create a valid transfer.
        '''
        return (self.execution_date and self.remote_account and
                self.transferred_amount and True) or False


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
        country_code -> the two letter ISO code of the country this parser is
                        built for: used to recreate country when new partners
                        are auto created
        doc  -> the description of the identifier. Shown to the user.
                    Translatable.

        parse -> the method for the actual parsing.
    '''
    __metaclass__ = parser_type
    name = None
    code = None
    country_code = None
    doc = __doc__

    def normalize_identifier(self, account, identifier):
        """
        Strip any substantial part of the account number from
        the identifier, as well as the common prefix 'CAMT053'.
        """
        if identifier.upper().startswith('CAMT053'):
            identifier = identifier[7:]
        seq_matcher = SequenceMatcher(None, account, identifier)
        _a, start, length = seq_matcher.find_longest_match(
            0, len(account), 0, len(identifier))
        if length < 7:
            return identifier
        result = identifier[0:start] + \
            identifier[start + length:len(identifier)]
        while result and not result[0].isalnum():
            result = result[1:]
        return result

    def get_unique_statement_id(self, cr, base):
        name = base
        suffix = 1
        while True:
            cr.execute(
                "select id from account_bank_statement where name = %s",
                (name,))
            if not cr.rowcount:
                break
            suffix += 1
            name = "%s-%d" % (base, suffix)
        return name

    def get_unique_account_identifier(self, cr, account):
        """
        Get an identifier for a local bank account, based on the last
        characters of the account number with minimum length 3.
        The identifier should be unique amongst the company accounts

        Presumably, the bank account is one of the company accounts
        itself but importing bank statements for non-company accounts
        is not prevented anywhere else in the system so the 'account'
        param being a company account is not enforced here either.
        """
        def normalize(account_no):
            return re.sub(r'\s', '', account_no)

        account = normalize(account)
        cr.execute(
            """SELECT acc_number FROM res_partner_bank
               WHERE company_id IS NOT NULL""")
        accounts = [normalize(row[0]) for row in cr.fetchall()]
        tail_length = 3
        while tail_length <= len(account):
            tail = account[-tail_length:]
            if len([acc for acc in accounts if acc.endswith(tail)]) < 2:
                return tail
            tail_length += 1
        return account

    def parse(self, cr, data):
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

        If your bank does not provide transaction ids, take a high resolution
        and a repeatable algorithm for the numbering. For example the date can
        be used as a prefix. Adding a tracer (day resolution) can create
        uniqueness. Adding unique statement ids can add to the robustness of
        your transaction numbering.

        Just mind that users can create random (file)containers with
        transactions in it. Try not to depend on order of appearance within
        these files. If in doubt: sort.
        '''
        raise NotImplementedError(
            _('This is a stub. Please implement your own.')
        )
