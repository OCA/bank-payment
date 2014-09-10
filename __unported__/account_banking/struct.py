# -*- encoding: utf-8 -*-
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

'''
Define a struct class which behaves like a dict, but allows using
object.attr alongside object['attr'].
'''

__all__ = ['struct']


class struct(dict):
    '''
    Ease working with dicts. Allow dict.key alongside dict['key']
    '''
    def __setattr__(self, item, value):
        self.__setitem__(item, value)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def show(self, indent=0, align=False, ralign=False):
        '''
        PrettyPrint method. Aligns keys right (ralign) or left (align).
        '''
        if align or ralign:
            width = 0
            for key in self.iterkeys():
                width = max(width, len(key))
            alignment = ''
            if not ralign:
                alignment = '-'
            fmt = '%*.*s%%%s%d.%ds: %%s' % (
                indent, indent, '', alignment, width, width
            )
        else:
            fmt = '%*.*s%%s: %%s' % (indent, indent, '')
        for item in self.iteritems():
            print(fmt % item)
