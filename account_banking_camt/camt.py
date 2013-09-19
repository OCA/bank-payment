from lxml import etree
from datetime import datetime
import re
from openerp.osv.orm import except_orm
from account_banking.parsers import models
from account_banking.parsers.convert import str2date

bt = models.mem_bank_transaction

class transaction(models.mem_bank_transaction):

    def __init__(self, values, *args, **kwargs):
        super(transaction, self).__init__(*args, **kwargs)
        for attr in values:
                setattr(self, attr, values[attr])

    def is_valid(self):
        return not self.error_message

class parser(models.parser):
    code = 'CAMT'
    country_code = 'NL'
    name = 'Generic CAMT Format'
    doc = '''\
CAMT Format parser
'''

    def tag(self, node):
        """
        Return the tag of a node, stripped from its namespace
        """
        return node.tag[len(self.ns):]

    def assert_tag(self, node, expected):
        """
        Get node's stripped tag and compare with expected
        """
        assert self.tag(node) == expected, (
            "Expected tag '%s', got '%s' instead" %
            (self.tag(node), expected))

    def xpath(self, node, expr):
        """
        Wrap namespaces argument into call to Element.xpath():

        self.xpath(node, './ns:Acct/ns:Id')
        """
        return node.xpath(expr, namespaces={'ns': self.ns[1:-1]})

    def find(self, node, expr):
        """
        Like xpath(), but return first result if any or else False
        
        Return None to test nodes for being truesy
        """
        result = node.xpath(expr, namespaces={'ns': self.ns[1:-1]})
        if result:
            return result[0]
        return None

    def get_balance_type_node(self, node, balance_type):
        """
        :param node: BkToCstmrStmt/Stmt/Bal node
        :param balance type: one of 'OPBD', 'PRCD', 'ITBD', 'CLBD'
        """
        code_expr = './ns:Bal/ns:Tp/ns:CdOrPrtry/ns:Cd[text()="%s"]/../../..' % balance_type
        return self.xpath(node, code_expr)
    
    def parse_amount(self, node):
        """
        Parse an element that contains both Amount and CreditDebitIndicator
        
        :return: signed amount
        :returntype: float
        """
        sign = -1 if node.find(self.ns + 'CdtDbtInd').text == 'CRDT' else 1
        return sign * float(node.find(self.ns + 'Amt').text)
        
    def get_start_balance(self, node):
        """
        Find the (only) balance node with code OpeningBalance, or
        the only one with code 'PreviousClosingBalance'
        or the first balance node with code InterimBalance in
        the case of preceeding pagination.

        :param node: BkToCstmrStmt/Stmt/Bal node
        """
        nodes = (
            self.get_balance_type_node(node, 'OPBD') or
            self.get_balance_type_node(node, 'PRCD') or
            self.get_balance_type_node(node, 'ITBD'))
        return self.parse_amount(nodes[0])

    def get_end_balance(self, node):
        """
        Find the (only) balance node with code ClosingBalance, or
        the second (and last) balance node with code InterimBalance in
        the case of continued pagination.

        :param node: BkToCstmrStmt/Stmt/Bal node
        """
        nodes = (
            self.get_balance_type_node(node, 'CLBD') or
            self.get_balance_type_node(node, 'ITBD'))
        return self.parse_amount(nodes[-1])

    def parse_Stmt(self, node):
        """
        Parse a single Stmt node
        """
        statement = models.mem_bank_statement()
        statement.id = node.find(self.ns + 'Id').text
        statement.local_account = (
            self.xpath(node, './ns:Acct/ns:Id/ns:IBAN')[0].text
            if self.xpath(node, './ns:Acct/ns:Id/ns:IBAN')
            else self.xpath(node, './ns:Acct/ns:Id/ns:Othr/ns:Id')[0].text)
        statement.local_currency = self.xpath(node, './ns:Acct/ns:Ccy')[0].text
        statement.start_balance = self.get_start_balance(node)
        statement.end_balance = self.get_end_balance(node)
        number = 0
        for Ntry in self.xpath(node, './ns:Ntry'):
            transaction_detail = self.parse_Ntry(Ntry)
            if number == 0:
                # Take the statement date from the first transaction
                statement.date = str2date(
                    transaction_detail['execution_date'], "%Y-%m-%d")
            number += 1
            transaction_detail['id'] = str(number).zfill(4)
            statement.transactions.append(
                transaction(transaction_detail))
        return statement

    def get_entry_description(self, node):
        """
        :param node: Ntry node
        """
        codes = self.xpath(node, './ns:BkTxCd/ns:Prtry/ns:Cd')
        if codes:
            return codes[0].text
        return False

    def parse_Ntry(self, node):
        """
        :param node: Ntry node
        """
        entry_description = self.get_entry_description(node)
        entry_details = {
            'execution_date': self.xpath(node, './ns:BookgDt/ns:Dt')[0].text,
            'effective_date': self.xpath(node, './ns:ValDt/ns:Dt')[0].text,
            'transfer_type': bt.ORDER,
            'transferred_amount': self.parse_amount(node)
            }
        TxDtls = self.xpath(node, './ns:NtryDtls/ns:TxDtls')
        if len(TxDtls) == 1:
            vals = self.parse_TxDtls(TxDtls[0], entry_details)
        else:
            vals = entry_details
        return vals

    def get_party_values(self, TxDtls):
        """
        Determine to get either the debtor or creditor party node
        and extract the available data from it
        """
        vals = {}
        party_type = self.find(
            TxDtls, '../../ns:CdtDbtInd').text == 'CRDT' and 'Dbtr' or 'Cdtr'
        party_node = self.find(TxDtls, './ns:RltdPties/ns:%s' % party_type)
        account_node = self.find(TxDtls, './ns:RltdPties/ns:%sAcct/ns:Id' % party_type)
        bic_node = self.find(
            TxDtls,
            './ns:RltdAgts/ns:%sAgt/ns:FinInstnId/ns:BIC' % party_type)
        if party_node is not None:
            name_node = self.find(party_node, './ns:Nm')
            vals['remote_owner'] = name_node.text if name_node is not None else False
            country_node = self.find(party_node, './ns:PstlAdr/ns:Ctry')
            vals['remote_owner_country'] = (
                country_node.text if country_node is not None else False)
            address_node = self.find(party_node, './ns:PstlAdr/ns:AdrLine')
            vals['remote_owner_address'] = (
                address_node.text if address_node is not None else False)
        if account_node is not None:
            iban_node = self.find(account_node, './ns:IBAN')
            if iban_node is not None:
                vals['remote_account'] = iban_node.text
                if bic_node is not None:
                    vals['remote_iban'] = bic_node.text
            else:
                domestic_node = self.find(account_node, './ns:Othr/ns:Id')
                vals['remote_account'] = (
                    domestic_node.text if domestic_node is not None else False)
        return vals

    def parse_TxDtls(self, TxDtls, entry_values):
        """
        Parse a single TxDtls node
        """
        vals = dict(entry_values)
        unstructured = self.xpath(TxDtls, './ns:RmtInf/ns:Ustrd')
        if unstructured:
            vals['message'] = ' '.join([x.text for x in unstructured])
        structured = self.find(TxDtls, './ns:RmtInf/ns:Strd/ns:CdtrRefInf/ns:Ref')
        if structured is not None:
            vals['reference'] = structured.text
        else:
            if vals.get('message') and re.match('^[^\s]+$', vals['message']):
                vals['reference'] = vals['message']
        vals.update(self.get_party_values(TxDtls))
        return vals

    def check_version(self):
        """
        Sanity check the document's namespace
        """
        if not self.ns.startswith('{urn:iso:std:iso:20022:tech:xsd:camt.'):
            raise except_orm(
                "Error",
                "This does not seem to be a CAMT format bank statement.")

        if not self.ns.startswith('{urn:iso:std:iso:20022:tech:xsd:camt.053.'):
            raise except_orm(
                "Error",
                "Only CAMT.053 is supported at the moment.")
        return True

    def parse(self, cr, data):
        """
        Parse a CAMT053 XML file
        """
        root = etree.fromstring(data)
        self.ns = root.tag[:root.tag.index("}") + 1]
        self.check_version()
        self.assert_tag(root[0][0], 'GrpHdr')
        statements = []
        for node in root[0][1:]:
            statements.append(self.parse_Stmt(node))
        return statements
