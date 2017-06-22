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

    @mock.patch('lib.input.requests.Session.get')
    def test_error_handling(self, m_get):
        m_get.side_effect = self.m_get

        # Nominal, should return 200
        resp = self.app.get('/28/office/complies/2017-02-19?beta=enabled')
        self.assertEqual(200, resp.status_code)

        # Fallback path (was completely broken on 2017-02-18)
        FakeResponse.status_code = 200
        resp = self.app.get('/28/office/complies/2017-02-18?beta=enabled')
        self.assertEqual(200, resp.status_code)
        self.assertIn("<source>website</source>", resp.data)

        # 404
        FakeResponse.status_code = 404
        resp = self.app.get('/28/office/complies/2017-02-19?beta=enabled')
        self.assertEqual(200, resp.status_code)
        self.assertIn("(404)", resp.data)

        # Teapot
        FakeResponse.status_code = 419
        resp = self.app.get('/28/office/complies/2017-02-19?beta=enabled')
        self.assertEqual(200, resp.status_code)
        self.assertIn("(419)", resp.data)

    @mock.patch('server.do_get_office')
    def test_get_meta(self, m_do_get_office):
        def mock_get_office(*args):
            return {'source': 'mock'}
        m_do_get_office.side_effect = mock_get_office

        # Test: key to office translation
        for office, key in keys.KEYS.iteritems():
            self.assertIn("<source>mock</source>", self.app.get('/01/02/2016/'+key).data)
            m_do_get_office.assert_called_once_with(0, 'prod', office, datetime.date(2016, 02, 01), 'romain')
            m_do_get_office.reset_mock()

        # Test: version+beta forwarding
        self.assertIn("<source>mock</source>", self.app.get('/01/02/2016/'+key+'?version=19&beta=1').data)
        m_do_get_office.assert_called_once_with(19, 'beta', office, datetime.date(2016, 02, 01), 'romain')
        m_do_get_office.reset_mock()


