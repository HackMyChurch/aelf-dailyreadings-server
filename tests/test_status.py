# -*- coding: utf-8 -*-

import mock

from base import TestBase, FakeResponse

class TestStatus(TestBase):
    def tearDown(self):
        FakeResponse.status_code = 200

    @mock.patch('server.datetime.date')
    @mock.patch('lib.input.requests.Session.get')
    def test_status(self, m_get, m_date):
        m_get.side_effect = self.m_get
        m_date.today.return_value = m_date
        m_date.year = 2017
        m_date.month = 4
        m_date.day = 16

        # Nominal, should return 200
        resp = self.app.get('/status')
        self.assertEqual(200, resp.status_code)

