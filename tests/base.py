# -*- coding: utf-8 -*-

import os
import unittest
import server
import mock
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
        path = './test_fixtures/'+url.replace('/', ':')
        res = FakeResponse()
        try:
            with open(path, 'r') as f:
                res.text = f.read()
        except:
            if 'AELF_DEBUG' not in os.environ:
                raise
            res.text = request_get(url, **kwargs).text
            with open(path, 'w') as f:
                f.write(res.text.encode('utf8'))

        return res

    def setUp(self):
        def fakeCallback(*args, **kwargs):
            return None

        self.app = server.app.test_client()
        self.app.debug = True
        self.app.config = {}
        self.app.import_name = "unittests"
        self.app.before_request = fakeCallback

