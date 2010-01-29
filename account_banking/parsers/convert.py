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

__all__ = ['str2date', 'date2str', 'date2date']

try:
    from datetime import datetime
    datetime.strptime
except AttributeError:
    from mx import DateTime as datetime

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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
