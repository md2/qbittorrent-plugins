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
import lxml.html
import tempfile
import traceback
import urllib
import urllib2
from time import time


class rutracker_org(object):
    url = 'http://rutracker.org'
    name = 'rutracker.org'

    supported_categories = {'all': ''}

    login_url = 'http://login.rutracker.org/forum/login.php'
    download_url = ''

    login_name = ''
    login_password = ''

    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0a2) Gecko/20111101 Firefox/9.0a2'

    domain = '.rutracker.org'
    prefix = 'RT: '

    exc_log = '/tmp/rutracker_org_exception.log'

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
            opener.open(self.login_url,
                        urllib.urlencode({'login_username': self.login_name,
                                          'login_password': self.login_password,
                                          'ses_short': 1,
                                          'login': '\xc2\xf5\xee\xe4'}))

    def download_torrent(self, url):
        try:
            self._sign_in()
            opener = self._opener
            cj = self._cj
            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
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
                cj.set_cookie(cookie)
                data = opener.open(url).read()
                tmpfile.write(data)
                name = tmpfile.name
            print name, url
        except Exception:
            try:
                with open(self.exc_log, 'a') as fo:
                    fo.write(traceback.format_exc())
            except Exception:
                pass

    def search(self, what, cat='all'):
        try:
            self._sign_in()
            opener = self._opener
            data = opener.open(self.url + '/forum/tracker.php?nm=%s' % (urllib.quote(what.decode('utf8').encode('cp1251'))))\
                         .read()
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
        except Exception:
            try:
                with open(self.exc_log, 'a') as fo:
                    fo.write(traceback.format_exc())
            except Exception:
                pass


if __name__ == '__main__':
    pass

