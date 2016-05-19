# -*- coding: utf-8 -*-

import os
import unittest
import server
import mock
from bs4 import BeautifulSoup

class FakeResponse(object): pass

class TestBase(unittest.TestCase):
    def assertItemsEqual(self, items, data):
        xml_items = BeautifulSoup(data, 'xml').find_all('item')
        self.assertEqual(len(items), len(xml_items))
        for i, xml_item in enumerate(xml_items):
            self.assertEqual(items[i][0], xml_item.title.text.strip())
            self.assertEqual(items[i][1], xml_item.description.text.strip())

    def assertMetaEqual(self, date, meta):
        resp = self.app.get('/v0/office/meta/'+date)
        self.assertEqual(200, resp.status_code)
        return self.assertItemsEqual([(u"Jour liturgique", meta)], resp.data)

    def m_get(self, url):
        url = url.replace('/', ':')
        path = './test_fixtures/'+url
        res = FakeResponse()
        with open(path, 'r') as f:
            res.text = f.read()
        return res

    def setUp(self):
        self.app = server.app.test_client()

