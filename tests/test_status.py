# -*- coding: utf-8 -*-

import os
import server
import keys
import mock
import datetime
from bs4 import BeautifulSoup

from base import TestBase, FakeResponse

class TestRouteCompat(TestBase):
    def tearDown(self):
        FakeResponse.status_code = 200

    @mock.patch('server.time.strftime')
    def test_status(self, m_strftime):
        m_strftime.return_value = "2017:04:15"

        # Nominal, should return 200
        resp = self.app.get('/status')
        self.assertEqual(200, resp.status_code)

