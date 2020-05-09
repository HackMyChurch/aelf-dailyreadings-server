# -*- coding: utf-8 -*-

import os
import server
import keys
import mock
import datetime
from bs4 import BeautifulSoup

from base import TestBase, FakeResponse

EXPECTED_ETAG = '6d90b712de6c68ed0e866b32ab87ba4e08008c53851095b8d49f7d2b335ba08a'

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

