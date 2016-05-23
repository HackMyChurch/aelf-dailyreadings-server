# -*- coding: utf-8 -*-

import os
import unittest
import server
import mock
from bs4 import BeautifulSoup

class FakeResponse(object): pass

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

    def m_get(self, url):
        url = url.replace('/', ':')
        path = './test_fixtures/'+url
        res = FakeResponse()
        with open(path, 'r') as f:
            res.text = f.read()
        return res

    def setUp(self):
        self.app = server.app.test_client()

