# -*- encoding: utf-8 -*-
##############################################################################
#
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

from account_banking import record

__all__ = ['IncassoBatch', 'BetalingsBatch', 'Incasso', 'Betaling',
           'IncassoFile', 'BetalingsFile', 'SalarisFile',
           'SalarisbetalingsOpdracht', 'BetalingsOpdracht', 'IncassoOpdracht',
           'OpdrachtenFile',
          ]

def elfproef(s):
    '''
    Dutch elfproef for validating 9-long local bank account numbers.
    '''
    r = 0
    l = len(s)
    for i,c in enumerate(s):
        r += (l-i) * int(c)
    return (r % 11) == 0

class HeaderRecord(record.Record): #{{{
   '''ClieOp3 header record'''
    _fields = [
        record.Filler('recordcode', 4, '0001'),
        record.Filler('variantcode', 1, 'A'),
        record.DateField('aanmaakdatum', '%d%m%y', auto=True),
        record.Filler('bestandsnaam', 8, 'CLIEOP03'),
        record.Field('inzender_id', 5),
        record.Field('bestands_id', 4),
        record.Field('duplicaatcode', 1),
        record.Filler('filler', 21),
    ]

    def __init__(self, id='1', volgnr=1, duplicate=False):
        super(HeaderRecord, self).__init__()
        self.inzender_id = id
        self.bestands_id = '%02d%02d' % (self.aanmaakdatum.day, volgnr)
        self.duplicaatcode = duplicate and '2' or '1'
#}}}

class FooterRecord(record.Record):
    '''ClieOp3 footer record'''
    _fields = [
        record.Filler('recordcode', 4, '9999'),
        record.Filler('variantcode', 1, 'A'),
        record.Filler('filler', 45),
    ]

class BatchHeaderRecord(record.Record):
    '''Header record preceding new batches'''
    _fields = [
        record.Filler('recordcode', 4, '0010'),
        record.Field('variantcode', 1),
        record.Field('transactiegroep', 2),
        record.NumberField('rekeningnr_opdrachtgever', 10),
        record.NumberField('batchvolgnummer', 4),
        record.Filler('aanlevermuntsoort', 3, 'EUR'),
        record.Field('batch_id', 16),
        record.Filler('filler', 10),
    ]

class BatchFooterRecord(record.Record):
    '''Closing record for batches'''
    _fields = [
        record.Filler('recordcode', 4, '9990'),
        record.Filler('variantcode', 1, 'A'),
        record.NumberField('totaalbedrag', 18),
        record.NumberField('totaal_rekeningnummers', 10),
        record.NumberField('aantal_posten', 7),
        record.Filler('filler', 10),
    ]

class VasteOmschrijvingRecord(record.Record):
    '''Fixed message'''
    _fields = [
        record.Filler('recordcode', 4, '0020'),
        record.Filler('variantcode', 1, 'A'),
        record.Field('vaste_omschrijving', 32),
        record.Filler('filler', 13),
    ]

class OpdrachtgeverRecord(record.Record):
    '''Ordering party'''
    _fields = [
        record.Filler('recordcode', 4, '0030'),
        record.Filler('variantcode', 1, 'B'),
        record.Field('NAWcode', 1),
        record.DateField('gewenste_verwerkingsdatum', '%d%m%y', auto=True),
        record.Field('naam_opdrachtgever', 35),
        record.Field('testcode', 1),
        record.Filler('filler', 2),
    ]

class TransactieRecord(record.Record):
    '''Transaction'''
    _fields = [
        record.Filler('recordcode', 4, '0100'),
        record.Filler('variantcode', 1, 'A'),
        record.NumberField('transactiesoort', 4),
        record.NumberField('bedrag', 12),
        record.NumberField('rekeningnr_betaler', 10),
        record.NumberField('rekeningnr_begunstigde', 10),
        record.Filler('filler', 9),
    ]

class NaamBetalerRecord(record.Record):
    '''Name payer'''
    _fields = [
        record.Filler('recordcode', 4, '0110'),
        record.Filler('variantcode', 1, 'B'),
        record.Field('naam', 35),
        record.Filler('filler', 10),
    ]

class BetalingskenmerkRecord(record.Record):
    '''Payment reference'''
    _fields = [
        record.Filler('recordcode', 4, '0150'),
        record.Filler('variantcode', 1, 'A'),
        record.Field('betalingskenmerk', 16),
        record.Filler('filler', 29),
    ]

class OmschrijvingRecord(record.Record):
    '''Description'''
    _fields = [
        record.Filler('recordcode', 4, '0160'),
        record.Filler('variantcode', 1, 'B'),
        record.Field('omschrijving', 32),
        record.Filler('filler', 13),
    ]

class NaamBegunstigdeRecord(record.Record):
    '''Name receiving party'''
    _fields = [
        record.Filler('recordcode', 4, '0170'),
        record.Filler('variantcode', 1, 'B'),
        record.Field('naam', 35),
        record.Filler('filler', 10),
    ]

class OpdrachtRecord(record.Record):
    '''Order details'''
    _fields = [
        record.Filler('recordcode', 6, 'KAE092'),
        record.Field('naam_transactiecode', 18),
        record.NumberField('totaalbedrag', 13),
        record.Field('rekeningnr_opdrachtgever', 10),
        record.NumberField('totaal_rekeningnummers', 5),
        record.NumberField('aantal_posten', 6),
        record.Field('identificatie', 6),
        record.DateField('gewenste_verwerkingsdatum', '%y%m%d'),
        record.Field('batch_medium', 18),
        record.Filler('muntsoort', 3, 'EUR'),
        record.Field('testcode', 1),
    ]
    def __init__(self, *args, **kwargs):
        super(OpdrachtRecord, self).__init__(*args, **kwargs)
        self.batch_medium = 'DATACOM'
        self.naam_transactiecode = self._transactiecode

class SalarisbetalingsOpdracht(OpdrachtRecord):
    '''Salary payment batch record'''
    _transactiecode = 'SALARIS'

class BetalingsOpdracht(OpdrachtRecord):
    '''Payment batch record'''
    _transactiecode = 'CREDBET'

class IncassoOpdracht(OpdrachtRecord):
    '''Direct debit payments batch record'''
    _transactiecode = 'INCASSO'

class Optional(object):
    '''Auxilliary class to handle optional records'''
    def __init__(self, klass, max=1):
        self._klass = klass
        self._max = max
        self._guts = []

    def __setattr__(self, attr, value):
        '''Check for number of records'''
        if attr[0] == '_':
            super(Optional, self).__setattr__(attr, value)
        else:
            if self._guts and len(self._guts) > self._max:
                raise ValueError, 'Only %d lines are allowed' % self._max
            newitem = self._klass()
            setattr(newitem, attr, value)
            self._guts.append(newitem)

    def __getattr__(self, attr):
        '''Only return if used'''
        if attr[0] == '_':
            return super(Optional, self).__getattr__(attr)
        return [getattr(x, attr) for x in self._guts]

    def __iter__(self):
        '''Make sure to adapt'''
        return self._guts.__iter__()

class OpdrachtenFile(object):
    '''A payment orders file'''
    def __init__(self, *args, **kwargs):
        self.opdrachten = []

    @property
    def rawdata(self):
        '''
        Return a writeable file content object
        '''
        return '\r\n'.join(self.opdrachten)

class Transactie(object):
    '''Generic transaction class'''
    def __init__(self, soort=0, naam=None, referentie=None, omschrijvingen=[],
                 rekeningnr_begunstigde=None, rekeningnr_betaler=None,
                 bedrag=0
                ):
        self.transactie = TransactieRecord()
        self.betalingskenmerk = Optional(BetalingskenmerkRecord)
        self.omschrijving = Optional(OmschrijvingRecord, 4)
        self.transactie.transactiesoort = soort
        self.transactie.rekeningnr_begunstigde = rekeningnr_begunstigde
        self.transactie.rekeningnr_betaler = rekeningnr_betaler
        self.transactie.bedrag = int(bedrag * 100)
        if referentie:
            self.betalingskenmerk.betalingskenmerk = referentie
        for oms in omschrijvingen:
            self.omschrijving.omschrijving = oms
        self.naam.naam = naam

class Incasso(Transactie):
    '''Direct Debit Payment transaction'''
    def __init__(self, *args, **kwargs):
        reknr = kwargs['rekeningnr_betaler']
        kwargs['soort'] = len(reknr.lstrip('0')) <= 7 and 1002 or 1001
        self.naam = NaamBetalerRecord()
        super(Incasso, self).__init__(*args, **kwargs)

    @property
    def rawdata(self):
        '''
        Return self as writeable file content object
        '''
        items = [str(self.transactie)]
        if self.naam:
            items.append(str(self.naam))
        for kenmerk in self.betalingskenmerk:
            items.append(str(kenmerk))
        for omschrijving in self.omschrijving:
            items.append(str(omschrijving))
        return '\r\n'.join(items)

class Betaling(Transactie):
    '''Payment transaction'''
    def __init__(self, *args, **kwargs):
        reknr = kwargs['rekeningnr_begunstigde']
        if len(reknr.lstrip('0')) > 7:
            if not elfproef(reknr):
                raise ValueError, '%s is not a valid bank account' % reknr
        kwargs['soort'] = 5
        self.naam = NaamBegunstigdeRecord()
        super(Betaling, self).__init__(*args, **kwargs)

    @property
    def rawdata(self):
        '''
        Return self as writeable file content object
        '''
        items = [str(self.transactie)]
        for kenmerk in self.betalingskenmerk:
            items.append(str(kenmerk))
        if self.naam:
            items.append(str(self.naam))
        for omschrijving in self.omschrijving:
            items.append(str(omschrijving))
        return '\r\n'.join(items)

class SalarisBetaling(Betaling):
    '''Salary Payment transaction'''
    def __init__(self, *args, **kwargs):
        reknr = kwargs['rekeningnr_begunstigde']
        kwargs['soort'] = len(reknr.lstrip('0')) <= 7 and 3 or 8
        super(SalarisBetaling, self).__init__(*args, **kwargs)

class Batch(object):
    '''Generic batch class'''
    transactieclass = None

    def __init__(self, opdrachtgever, rekeningnr, verwerkingsdatum=None,
                 test=True, omschrijvingen=[], transactiegroep=None,
                 batchvolgnummer=1, batch_id=''
                ):
        self.header = BatchHeaderRecord()
        self.vaste_omschrijving = Optional(VasteOmschrijvingRecord, 4)
        self.opdrachtgever = OpdrachtgeverRecord()
        self.footer = BatchFooterRecord()
        self.header.variantcode = batch_id and 'C' or 'B'
        self.header.transactiegroep = transactiegroep
        self.header.batchvolgnummer = batchvolgnummer
        self.header.batch_id = batch_id
        self.header.rekeningnr_opdrachtgever = rekeningnr
        self.opdrachtgever.naam_opdrachtgever = opdrachtgever
        self.opdrachtgever.gewenste_verwerkingsdatum = verwerkingsdatum
        self.opdrachtgever.NAWcode = 1
        self.opdrachtgever.testcode = test and 'T' or 'P'
        self.transacties = []
        for omschrijving in omschrijvingen:
            self.vaste_omschrijving.omschrijving = omschrijving

    @property
    def aantal_posten(self):
        '''nr of posts'''
        return len(self.transacties)

    @property
    def totaalbedrag(self):
        '''total amount transferred'''
        return reduce(lambda x,y: x + int(y.transactie.bedrag),
                      self.transacties, 0
                     )

    @property
    def totaal_rekeningnummers(self):
        '''check number on account numbers'''
        return reduce(lambda x,y: 
                          x + int(y.transactie.rekeningnr_betaler) + \
                          int(y.transactie.rekeningnr_begunstigde),
                      self.transacties, 0
                     )

    @property
    def rawdata(self):
        '''
        Return self as writeable file content object
        '''
        self.footer.aantal_posten = self.aantal_posten
        self.footer.totaalbedrag = self.totaalbedrag
        self.footer.totaal_rekeningnummers = self.totaal_rekeningnummers
        lines = [str(self.header)]
        for oms in self.vaste_omschrijving:
            lines.append(str(oms))
        lines += [
            str(self.opdrachtgever),
            '\r\n'.join([x.rawdata for x in self.transacties]),
            str(self.footer)
        ]
        return '\r\n'.join(lines)

    def transactie(self, *args, **kwargs):
        '''generic factory method'''
        retval = self.transactieclass(*args, **kwargs)
        self.transacties.append(retval)
        return retval

class IncassoBatch(Batch):
    '''Direct Debig Payment batch'''
    transactieclass = Incasso

class BetalingsBatch(Batch):
    '''Payment batch'''
    transactieclass = Betaling

class SalarisBatch(Batch):
    '''Salary payment class'''
    transactieclass = SalarisBetaling

class ClieOpFile(object):
    '''The grand unifying class'''
    def __init__(self, identificatie='1', uitvoeringsdatum=None,
                 naam_opdrachtgever='', rekeningnr_opdrachtgever='',
                 test=False, **kwargs):
        self.header = HeaderRecord(id=identificatie,)
        self.footer = FooterRecord()
        self.batches = []
        self._uitvoeringsdatum = uitvoeringsdatum
        self._identificatie = identificatie
        self._naam_opdrachtgever = naam_opdrachtgever
        self._reknr_opdrachtgever = rekeningnr_opdrachtgever
        self._test = test

    @property
    def rawdata(self):
        '''Return self as writeable file content object'''
        return '\r\n'.join(
            [str(self.header)] +
            [x.rawdata for x in self.batches] +
            [str(self.footer)]
        )

    def batch(self, *args, **kwargs):
        '''Create batch'''
        kwargs['transactiegroep'] = self.transactiegroep
        kwargs['batchvolgnummer'] = len(self.batches) +1
        kwargs['verwerkingsdatum'] = self._uitvoeringsdatum
        kwargs['test'] = self._test
        args = (self._naam_opdrachtgever, self._reknr_opdrachtgever)
        retval = self.batchclass(*args, **kwargs)
        self.batches.append(retval)
        return retval

    @property
    def opdracht(self):
        '''Produce an order to go with the file'''
        totaal_rekeningnummers = 0
        totaalbedrag = 0
        aantal_posten = 0
        for batch in self.batches:
            totaal_rekeningnummers += batch.totaal_rekeningnummers
            totaalbedrag += batch.totaalbedrag
            aantal_posten += batch.aantal_posten
        retval = self.opdrachtclass()
        retval.identificatie = self._identificatie
        retval.rekeningnr_opdrachtgever = self._reknr_opdrachtgever
        retval.gewenste_verwerkingsdatum = self._uitvoeringsdatum
        retval.testcode = self._test and 'T' or 'P'
        retval.totaalbedrag = totaalbedrag
        retval.aantal_posten = aantal_posten
        retval.totaal_rekeningnummers = totaal_rekeningnummers
        return retval

class IncassoFile(ClieOpFile):
    '''Direct Debit Payments file'''
    transactiegroep = '10'
    batchclass = IncassoBatch
    opdrachtclass = IncassoOpdracht

class BetalingsFile(ClieOpFile):
    '''Payments file'''
    transactiegroep = '00'
    batchclass = BetalingsBatch
    opdrachtclass = BetalingsOpdracht

class SalarisFile(BetalingsFile):
    '''Salary Payments file'''
    batchclass = SalarisBatch
    opdrachtclass = SalarisbetalingsOpdracht

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

