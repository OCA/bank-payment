# -*- coding: utf-8 -*-
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
from datetime import datetime


__all__ = ['str2date', 'date2str', 'date2date', 'to_swift']


def str2date(datestr, format='%d/%m/%y'):
    '''Convert a string to a datatime object'''
    return datetime.strptime(datestr, format)


def date2str(date, format='%Y-%m-%d'):
    '''Convert a datetime object to a string'''
    return date.strftime(format)


def date2date(datestr, fromfmt='%d/%m/%y', tofmt='%Y-%m-%d'):
    '''
    Convert a date in a string to another string, in a different
    format
    '''
    return date2str(str2date(datestr, fromfmt), tofmt)


_SWIFT = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
          "/-?:().,'+ ")


def to_swift(astr, schemes=('utf-8', 'latin-1', 'ascii')):
    '''
    Reduce a string to SWIFT format
    '''
    if not isinstance(astr, unicode):
        for scheme in schemes:
            try:
                astr = unicode(astr, scheme)
                break
            except UnicodeDecodeError:
                pass
        if not isinstance(astr, unicode):
            return astr

    s = [x in _SWIFT and x or ' '
         for x in unicodedata.normalize('NFKD', astr).encode('ascii', 'ignore')
         ]
    return ''.join(s)
