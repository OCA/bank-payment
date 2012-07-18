# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Igor Cota (<http://www.codexapertus.hr>).
#	 Special thanks to Pythonic code stylist Thomas Perl (<http://thp.io>)
#
#    Copyright (C) 2010 Sami Haahtinen (<http://ressukka.net>).
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

'''
This parser implements the Raiffeisenbank Croatia XML format support.
'''
from account_banking.parsers import models
from tools.translate import _
import xml, datetime, time
from xml.dom.minidom import parseString

__all__ = ['parser']

def get_first_node(dom, *args):	
    '''
    Function to go down DOM hierarchy. Made for brevity.
    '''
    node = None
    for arg in args:
        if node == None:
            node = dom.getElementsByTagName(args[0])[0]
        else:
            node = node.getElementsByTagName(arg)[0]
    
    return node

class transaction(models.mem_bank_transaction):
    '''
    Implementation of transaction communication class for account_banking.
    '''
    def __init__(self, transaction_dom, *args, **kwargs):
        '''
        Parse specific transaction DOM and set attributes.
        '''
        iidd = get_first_node(transaction_dom, "BrojTransakcije").firstChild.nodeValue
        execution_date = datetime.datetime.strptime(get_first_node(transaction_dom, "DatumValute").firstChild.nodeValue, '%d.%m.%Y')
        effective_date = datetime.datetime.strptime(get_first_node(transaction_dom, "DatumKnjizenja").firstChild.nodeValue, '%d.%m.%Y')
        
        owner_string = get_first_node(transaction_dom, "DuznikPrimatelj_1").firstChild.nodeValue
        remote_owner = ' '.join(owner_string.split()) # Way too much random whitespace
        
        transferred_amount = 0. # Assume float
        
        if get_first_node(transaction_dom, 'Promet', 'Tip').firstChild.nodeValue == 'P':
			transferred_amount = float(get_first_node(transaction_dom, 'Promet', 'Iznos').firstChild.nodeValue.replace(',',''))
        else:
			transferred_amount = -float(get_first_node(transaction_dom, 'Promet', 'Iznos').firstChild.nodeValue.replace(',',''))
			
        super(transaction, self).__init__(*args, **kwargs) 
        
        self.id = iidd
        self.execution_date = execution_date
        self.effective_date = effective_date
        self.remote_owner = remote_owner
        self.transferred_amount = transferred_amount

    def is_valid(self):
        return True # Everything is fine. Trust me.

class statement(models.mem_bank_statement):
    '''
    Implementation of bank_statement communication class of account_banking
    '''
    def __init__(self, dom, *args, **kwargs):
        '''
        Parse DOM and set general statement attributes
        '''
        super(statement, self).__init__(*args, **kwargs)
        
        year = get_first_node(dom, "GodinaIzvoda").firstChild.nodeValue
        serial = get_first_node(dom, "BrojIzvoda").firstChild.nodeValue
        
        self.id = 'BNK/' + year + '/' + serial[1:]
        
        self.local_account = '2484008-' + get_first_node(dom, "Racun").firstChild.nodeValue # Prepend RBA VDBI
        self.local_currency = 'HRK' # Hardcoded HRK
        
        self.start_balance = float(get_first_node(dom, "Grupe", "Grupa", "ZaglavljeGrupe", "PocetnoStanje").firstChild.nodeValue.replace(',',''))      
        self.end_balance = float(get_first_node(dom, "Grupe", "Grupa", "ProknjizenoStanje", "Iznos").firstChild.nodeValue.replace(',',''))
        
        self.date = datetime.datetime.strptime(get_first_node(dom, "DatumIzvoda").firstChild.nodeValue, '%d.%m.%Y')

class parser(models.parser):
    code = 'HRRBA'
    country_code = 'hr'
    name = _('RBA statement format')
    doc = _('''RBA XML format defines one statement per file. This parser
will parse the file and import to OpenERP
''')

    def parse(self, data):
        result = []
        stmnt = None        
        dom = xml.dom.minidom.parseString(data)
     
        stmnt = statement(dom) # We have just the one statement per file

        for i in get_first_node(dom, 'Grupa', 'Stavke').getElementsByTagName('Stavka'):
			trnsact = transaction(i)
			stmnt.transactions.append(trnsact)
			
        result.append(stmnt)
        return result
