# -*- coding: utf-8 -*-

import os
import server
import keys
import mock
import datetime
from bs4 import BeautifulSoup

from base import TestBase, FakeResponse

EXPECTED_ETAG = '2c3dc24608778f3a8249cb1849c51471f546eb92bc08b30b7e6be08b384ba5bf'

class TestCache(TestBase):

    @mock.patch('lib.input.requests.Session.get')
    def test_get_laudes_47(self, m_get):
        m_get.side_effect = self.m_get

        # Warm up cache
        resp = self.app.get('/47/office/laudes/2018-01-28')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(EXPECTED_ETAG, resp.headers['Etag'])

        # Test cache miss
        resp = self.app.get('/47/office/laudes/2018-01-28', headers={'If-None-Match': 'miss'})
        self.assertEqual(200, resp.status_code)
        self.assertEqual(EXPECTED_ETAG, resp.headers['Etag'])

        # Test cache hit
        resp = self.app.get('/47/office/laudes/2018-01-28', headers={'If-None-Match': EXPECTED_ETAG})
        self.assertEqual(304, resp.status_code)

