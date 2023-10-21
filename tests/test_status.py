# -*- coding: utf-8 -*-

import server
import mock
from datetime import date
from bs4 import BeautifulSoup

from base import TestBase, FakeResponse

class TestRouteCompat(TestBase):
    def tearDown(self):
        FakeResponse.status_code = 200

    @mock.patch('status.datetime.date')
    @mock.patch('server.time.strftime')
    @mock.patch('lib.input.requests.Session.get')
    def test_status(self, m_get, m_strftime, m_date_today):
        m_get.side_effect = self.m_get
        m_strftime.return_value = "2017:04:15"
        m_date_today.today.return_value = date(2017, 4, 15)
        m_date_today.side_effect = lambda *args, **kw: date(*args, **kw)

        # Nominal, should return 200
        resp = self.app.get('/status')
        self.assertEqual(200, resp.status_code)

