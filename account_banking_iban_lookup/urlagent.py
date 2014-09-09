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
This module presents a browser like class to browse the web, fill and submit
forms and to parse the results back in. It is heavily based on BeautifulSoup.
'''

import urllib

__all__ = ['urlsplit', 'urljoin', 'pathbase', 'urlbase', 'SoupForm',
           'URLAgent'
           ]


def urlsplit(url):
    '''
    Split an URL into scheme, host and path parts. Helper function.
    '''
    if ':' in url:
        parts = url.split(':')
        scheme = parts[0]
        url = ':'.join(parts[1:])
    else:
        scheme = ''
    host, path = urllib.splithost(url)
    return (scheme, host, path)


def urljoin(scheme, host, path, args=None):
    '''
    Join scheme, host and path to a full URL.
    Optional: add urlencoded args.
    Helper function.
    '''
    url = '%s://%s/%s' % (scheme or 'http', host, path)
    if args:
        url += '?%s' % urllib.urlencode(args)
    return url


def pathbase(path):
    '''
    Return the base for the path in order to satisfy relative paths.
    Helper function.
    '''
    if path and '/' in path:
        return path[:path.rfind('/') + 1]
    return path


def urlbase(url):
    '''
    Return the base URL for url in order to satisfy relative paths.
    Helper function.
    '''
    scheme, host, path = urlsplit(url)
    return urljoin(scheme, host, pathbase(path))


class SoupForm(object):
    '''
    A SoupForm is a representation of a HTML Form in BeautifulSoup terms.
    It has a helper method __setitem__ to set or replace form fields.
    It gets initiated from a soup object.
    '''
    def __init__(self, soup, parent=False):
        '''
        Parse the form attributes and fields from the soup.  Make sure
        to get the action right.  When parent is set, then the parent
        element is used as anchor for the search for form elements.
        '''
        self._extra_args = {}
        self.soup = soup

        # Make sure to use base strings, not unicode
        for attr, value in soup.attrMap.iteritems():
            setattr(self, str(attr), str(value))

        # Set right anchor point for harvest
        if parent:
            self.soup = soup.parent

        # Harvest input elements.
        self._args = {}
        for item in self.soup.findAll('input'):
            # Make sure to initialize to '' to avoid None strings to appear
            # during submit
            self._args[str(item.get('name'))] = item.get('value') or ''

        # Harvest url
        self.scheme, self.host, self.action = urlsplit(self.action)
        self.action, args = urllib.splitquery(self.action)
        if args:
            args = args.split('&')
            for arg in args:
                attr, value = urllib.splitvalue(arg)
                self._extra_args[str(attr)] = value or ''

    def __setitem__(self, name, value, force=False):
        '''
        Set values for the form attributes when present
        '''
        if name in self._args or force:
            self._extra_args[name] = value
        else:
            raise AttributeError('No such attribute: %s' % name)

    def __getitem__(self, name):
        '''
        Get a value. Set values overrule got values.
        '''
        if name in self._extra_args:
            return self._extra_args[name]
        if name in self._args:
            return self._args[name]
        raise AttributeError('No attribute with name "%s" found.' % name)

    def set(self, **kwargs):
        '''
        Forcibly sets an attribute to the supplied value, even if it is not
        part of the parsed form.
        Can be useful in situations where forms are deliberatly chunked in
        order to make it difficult to automate form requests, e.g. the
        SWIFT BIC service, which uses JavaScript to add form attributes to an
        emtpy base form.
        '''
        for name, value in kwargs.iteritems():
            self.__setitem__(name, value, force=True)

    def args(self):
        '''
        Return the field values as attributes, updated with the modified
        values.
        '''
        args = dict(self._args)
        args.update(self._extra_args)
        return args


class URLAgent(object):
    '''
    Assistent object to ease HTTP(S) requests.
    Mimics a normal web browser.
    '''

    def __init__(self, *args, **kwargs):
        super(URLAgent, self).__init__(*args, **kwargs)
        self._extra_headers = {}
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (X11; U; Linux x86_64; us; rv:1.9.0.10) '
                'Gecko/2009042708 Fedora/3.0.10-1.fc9 Firefox/3.0.10'),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;'
                'q=0.9,*/*;q=0.8'),
            'Accept-Language': 'en-us;q=1.0',
            'Accept-Charset': 'UTF-8,*',
            'Cache-Control': 'max-age=0'
        }

    def add_headers(self, **kwargs):
        self._extra_headers.update(**kwargs)

    def open(self, URL):
        '''
        Open a URL and set some vars based on the used URL.
        Meant to be used on a single server.
        '''
        self.scheme, self.host, self.path = urlsplit(URL)

        # Create agent
        self.agent = urllib.URLopener()

        # Remove additional and unasked for User-Agent header
        # Some servers choke on multiple User-Agent headers
        self.agent.addheaders = []
        headers = self._extra_headers.copy()
        headers.update(self.headers)
        for key, value in headers.iteritems():
            self.agent.addheader(key, value)

        # Open webpage
        request = self.agent.open(URL)

        # Get and set cookies for next actions
        attributes = request.info()
        if 'set-cookie' in attributes:
            self.agent.addheader('Cookie', attributes['set-cookie'])

        # Add referer
        self.agent.addheader('Referer', URL)

        # Return request
        return request

    def submit(self, form, action=None, method=None, **kwargs):
        '''
        Submit a SoupForm. Override missing attributes in action from our own
        initial URL.
        '''
        if action:
            scheme, host, path = urlsplit(action)
        else:
            scheme = form.scheme or self.scheme
            host = form.host or self.host
            action = form.action
        method = (method or form.method).lower()
        args = urllib.urlencode(kwargs or form.args())

        if not action.startswith('/'):
            # Relative path
            action = pathbase(self.path) + action

        function = getattr(self.agent, 'open_%s' % scheme)
        if method == 'post':
            return function('//%s%s' % (host, action), args)
        return function('//%s%s?%s' % (host, action, args))
