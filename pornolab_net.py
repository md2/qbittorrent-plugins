# -*- coding: utf-8 -*-
#VERSION: 1.00
#AUTHORS: root (root@localhost)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

try:
    from novaprinter import prettyPrinter
except ImportError:
    def prettyPrinter(dict_):
        print u'{link}|{name}|{size}|{seeds}|{leech}|{engine_url}'.format(**dict_)\
                                                                  .encode('utf8')

import cookielib
import glob
import lxml.html
import os
import re
import sqlite3
import tempfile
import traceback
import urllib
import urllib2
from time import time


class pornolab_net(object):
    url = 'http://pornolab.net'
    name = 'pornolab.net'

    supported_categories = {'all': ''}

    login_url = 'http://pornolab.net/forum/login.php'
    download_url = 'http://pornolab.net/forum/'

    login_name = ''
    login_password = ''

    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0a2) Gecko/20111101 Firefox/9.0a2'

    domain = '.pornolab.net'
    prefix = 'PL: '

    exc_log = '/tmp/pornolab_net_exception.log'

    def __init__(self):
        self._cj = cookielib.MozillaCookieJar()
        self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._cj))
        self._opener.addheaders = [('User-Agent', self.ua)]

    def _sign_in(self):
        cj = self._cj
        opener = self._opener
        if opener.open(self.url + '/forum/index.php')\
                 .read()\
                 .find('>\xc2\xfb\xf5\xee\xe4<') == -1:
            conn = sqlite3.connect(glob.glob(os.path.expanduser('~/.mozilla/firefox/*.default/cookies.sqlite'))[0])
            cur = conn.cursor()
            cur.execute("select host, path, isSecure, expiry, name, value from moz_cookies where basedomain = 'pornolab.net'")
            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
                tmpfile.write('''\
# Netscape HTTP Cookie File
# http://www.netscape.com/newsref/std/cookie_spec.html
# This is a generated file!  Do not edit.
''')
                for row in cur.fetchall():
                    tmpfile.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (row[0], row[0].startswith('.') and 'TRUE' or 'FALSE',
                                                                    row[1], row[2] and 'TRUE' or 'FALSE', row[3], row[4],
                                                                    row[5]))
                tmpfile.close()
                cj.load(tmpfile.name)
                os.unlink(tmpfile.name)

    def download_torrent(self, url):
        try:
            self._sign_in()
            cookie = cookielib.Cookie(
                version = 0,
                name = 'bb_dl',
                value = url.split('=')[-1],
                port = None,
                port_specified = False,
                domain = self.domain,
                domain_specified = True,
                domain_initial_dot = True,
                path = '/forum/',
                path_specified = True,
                secure = False,
                expires = int(time()) + 5 * 60,
                discard = False,
                comment = None,
                comment_url = None,
                rest = {'http_only': None}
            )
            self._cj.set_cookie(cookie)
            data = self._opener.open(url).read()
            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
                tmpfile.write(data)
                name = tmpfile.name
            print name, url
        except Exception:
            try:
                with open(self.exc_log, 'a') as fo:
                    fo.write(traceback.format_exc())
            except Exception:
                pass

    def _parse_document(self, data):
        document = lxml.html.document_fromstring(data)
        info = {'engine_url': self.url}
        for t in document.cssselect('tr.tCenter'):
            try:
                a = t.xpath('.//a[contains(@href,"dl.php?t=")]')[0]
                info.update(
                    name = (self.prefix
                            + t.xpath('.//a[contains(@href,"tracker.php?f=")]')[0].text_content()
                            + ' - '
                            + t.xpath('.//a[contains(@href,"viewtopic.php?t=")]')[0].text_content()),
                    link = self.download_url + a.attrib['href'],
                    size = a.text_content().replace(u'\xa0', ' ').replace(u' \u2193', ''),
                    seeds = t.xpath('.//td[contains(@class,"seed")]')[0].text_content(),
                    leech = t.xpath('.//td[contains(@class,"leech")]')[0].text_content()
                )
                prettyPrinter(info)
            except IndexError:
                pass

    def search(self, what, cat='all'):
        try:
            self._sign_in()
            opener = self._opener
            search_url = self.url + '/forum/tracker.php?nm=%s' % (urllib.quote(what.decode('utf8').encode('cp1251')))
            data = opener.open(search_url)\
                         .read()
            self._parse_document(data)

            re_page = re.compile(u'\xd1\xf2\xf0\xe0\xed\xe8\xf6\xe0 <b>1</b> \xe8\xe7 <b>(\d+)</b>')
            m =  re_page.search(data)
            if m:
                page_count = int(m.group(1))
                re_search_id = re.compile('search_id=([0-9a-zA-Z]+)')
                m = re_search_id.search(data)
                if m:
                    search_id = m.group(1)
                    for start in range(50, page_count*50, 50):
                        url = search_url + '&search_id=' + search_id + '&start=' + str(start)
                        data = opener.open(url).read()
                        self._parse_document(data)
        except Exception:
            try:
                with open(self.exc_log, 'a') as fo:
                    fo.write(traceback.format_exc())
            except Exception:
                pass


if __name__ == '__main__':
    pass

