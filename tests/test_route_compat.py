# -*- coding: utf-8 -*-

import os
import server
import keys
import mock
from bs4 import BeautifulSoup

from base import TestBase

class TestRouteCompat(TestBase):
    @mock.patch('server.do_get_office')
    def test_get_meta(self, m_do_get_office):
        def mock_get_office(*args):
            return "OK"
        m_do_get_office.side_effect = mock_get_office

        for office, key in keys.KEYS.iteritems():
            self.assertEqual("OK", self.app.get('/01/02/2016/'+key).data)
            m_do_get_office.assert_called_once_with(0, office, 1, 2, 2016)
            m_do_get_office.reset_mock()

