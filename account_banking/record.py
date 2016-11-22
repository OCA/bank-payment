# coding: utf-8
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import unicodedata
from datetime import datetime, date


__all__ = [
    'Field', 'Filler', 'DateField', 'NumberField', 'RightAlignedField',
    'RecordType', 'Record', 'asciify'
]

__doc__ = '''Ease working with fixed length records in files'''


def strpdate(str, format):
    return datetime.strptime(str, format).date()


class Field(object):
    '''Base Field class - fixed length left aligned string field in a record'''
    def __init__(self, name, length=1, fillchar=' ', cast=str):
        self.name = name.replace(' ', '_')
        self.length = length
        self.fillchar = fillchar
        self.cast = cast

    def format(self, value):
        value = self.cast(value)
        if len(value) > self.length:
            return value[:self.length]
        return value.ljust(self.length, self.fillchar)

    def take(self, buffer):
        offset = hasattr(self, 'offset') and self.offset or 0
        return self.cast(buffer[offset:offset + self.length].rstrip(
            self.fillchar)
        )

    def __repr__(self):
        return '%s "%s"' % (self.__class__.__name__, self.name)


class Filler(Field):
    '''Constant value field'''
    def __init__(self, name, length=1, value=' '):
        super(Filler, self).__init__(name, length, cast=str)
        self.value = str(value)

    def take(self, buffer):
        return self.format(buffer)

    def format(self, value):
        return super(Filler, self).format(
            self.value * (self.length / len(self.value) + 1)
        )


class DateField(Field):
    '''Variable date field'''
    def __init__(self, name, format='%Y-%m-%d', auto=False, cast=str):
        length = len(date.today().strftime(format))
        super(DateField, self).__init__(name, length, cast=cast)
        self.dateformat = format
        self.auto = auto

    def format(self, value):
        if isinstance(value, (str, unicode)) and \
           len(value.strip()) == self.length:
            value = strpdate(value, self.dateformat)
        elif not isinstance(value, (datetime, date)):
            value = date.today()
        return value.strftime(self.dateformat)

    def take(self, buffer):
        value = super(DateField, self).take(buffer)
        if value:
            return strpdate(value, self.dateformat)
        return self.auto and date.today() or None


class RightAlignedField(Field):
    '''Deviation of Field: right aligned'''
    def format(self, value):
        if len(value) > self.length:
            return value[-self.length:]
        return value.rjust(self.length, self.fillchar)

    def take(self, buffer):
        offset = hasattr(self, 'offset') and self.offset or 0
        return self.cast(buffer[offset:offset + self.length].lstrip(
            self.fillchar)
        )


class NumberField(RightAlignedField):
    '''Deviation of Field: left zero filled'''
    def __init__(self, *args, **kwargs):
        kwargs['fillchar'] = '0'
        super(NumberField, self).__init__(*args, **kwargs)

    def format(self, value):
        return super(NumberField, self).format(self.cast(value or ''))


class RecordType(object):
    fields = []

    def __init__(self, fields=()):
        if fields:
            self.fields = fields
        offset = 0
        for field in self.fields:
            field.offset = offset
            offset += field.length

    def __len__(self):
        return reduce(lambda x, y: x + y.length, self.fields, 0)

    def __contains__(self, key):
        return any(lambda x, y=key: x.name == y, self.fields)

    def __getitem__(self, key):
        for field in self.fields:
            if field.name == key:
                return field
        raise KeyError('No such field: %s' % key)

    def format(self, buffer):
        result = []
        for field in self.fields:
            result.append(field.format(field.take(buffer)))
        return ''.join(result)

    def take(self, buffer):
        return dict(zip([x.name for x in self.fields],
                        [x.take(buffer) for x in self.fields]
                        ))


class Record(object):
    _recordtype = None

    def __init__(self, recordtype=None, value=''):
        if hasattr(self, '_fields') and self._fields:
            self._recordtype = RecordType(self._fields)
        if not self._recordtype and not recordtype:
            raise ValueError('No recordtype specified')
        if not self._recordtype:
            self._recordtype = recordtype()
        self._length = len(self._recordtype)
        self._value = value.ljust(self._length)[:self._length]

    def __len__(self):
        return self._length

    def __setattr__(self, attr, value):
        if attr.startswith('_'):
            super(Record, self).__setattr__(attr, value)
        else:
            field = self._recordtype[attr]
            self._value = (
                self._value[:field.offset] +
                field.format(value) +
                self._value[field.offset + field.length:]
            )

    def __getattr__(self, attr):
        if attr.startswith('_'):
            return super(Record, self).__getattr__(attr)
        field = self._recordtype[attr]
        return field.take(self._value)

    def __str__(self):
        return self._recordtype.format(self._value)

    def __unicode__(self):
        return unicode(self.cast(self))


def asciify(str):
    return unicodedata.normalize('NFKD', str).encode('ascii', 'ignore')
