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
        self.assertEqual('c9acb612a00765b8b42e8e03243cb757baf6166f53300691cd4cd9747f46aeec', resp.headers['Etag'])

        # Test cache miss
        resp = self.app.get('/47/office/laudes/2018-01-28', headers={'If-None-Match': 'miss'})
        self.assertEqual(200, resp.status_code)
        self.assertEqual('c9acb612a00765b8b42e8e03243cb757baf6166f53300691cd4cd9747f46aeec', resp.headers['Etag'])

        # Test cache hit
        resp = self.app.get('/47/office/laudes/2018-01-28', headers={'If-None-Match': 'c9acb612a00765b8b42e8e03243cb757baf6166f53300691cd4cd9747f46aeec'})
        self.assertEqual(304, resp.status_code)

