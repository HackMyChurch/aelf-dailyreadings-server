# -*- coding: utf-8 -*-

import os
import server
import keys
import mock
import datetime
from bs4 import BeautifulSoup

from base import TestBase, FakeResponse

class TestCache(TestBase):

    @mock.patch('lib.input.requests.Session.get')
    def test_get_laudes_47(self, m_get):
        m_get.side_effect = self.m_get

        # Warm up cache
        resp = self.app.get('/47/office/laudes/2018-01-28')
        self.assertEqual(200, resp.status_code)
        self.assertEqual('02ec4a5e4fd668b0a099e75290ca1e9ecd857838df3f92d2031d8d8f3b86b52b', resp.headers['Etag'])

        # Test cache miss
        resp = self.app.get('/47/office/laudes/2018-01-28', headers={'If-None-Match': 'miss'})
        self.assertEqual(200, resp.status_code)
        self.assertEqual('02ec4a5e4fd668b0a099e75290ca1e9ecd857838df3f92d2031d8d8f3b86b52b', resp.headers['Etag'])

        # Test cache hit
        resp = self.app.get('/47/office/laudes/2018-01-28', headers={'If-None-Match': '02ec4a5e4fd668b0a099e75290ca1e9ecd857838df3f92d2031d8d8f3b86b52b'})
        self.assertEqual(304, resp.status_code)

