import os
import unittest
import server
import json
from requests import get as request_get
from bs4 import BeautifulSoup

class FakeResponse(object):
    status_code = 200
    text = ''

    def json(self, **kwargs):
        return json.loads(self.text, **kwargs)

class TestBase(unittest.TestCase):
    def parseItems(self, data):
        items = []
        for item in BeautifulSoup(data, 'xml').find_all('item'):
            items.append((
                item.title.text.strip(),
                item.description.text.strip(),
            ))
        return items

    def assertItemsEqual(self, items, data):
        expected = self.parseItems(data)
        self.assertEqual(expected, items)

    def m_get(self, url, **kwargs):
        '''
        Get a resource from fixtures. If AELF_DEBUG is defined and the resource can not be
        found, load it from the Internet and save it for future use. An existing resource
        will never be overwriten.
        '''
        filename = url.replace('/', ':')
        path = './test_fixtures/'+filename
        res = FakeResponse()
        try:
            with open(path, 'r') as f:
                res.text = f.read()
        except:
            if os.environ.get('AELF_DEBUG', '') in ['1', filename]:
                res.text = request_get(url, **kwargs).text
                with open(path, 'w') as f:
                    f.write(res.text)
            else:
                print(('Lecture not found, please set AELF_DEBUG="%s" to load it' % (filename)))
                res.text = ''

        return res

    def setUp(self):
        def fakeCallback(*args, **kwargs):
            return None

        self.app = server.app.test_client()
