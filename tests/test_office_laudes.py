# -*- coding: utf-8 -*-

import mock
from bs4 import BeautifulSoup

from base import TestBase

class TestOfficeLaudes(TestBase):
    @mock.patch('utils.requests.get')
    def test_get_laudes(self, m_get):
        m_get.side_effect = self.m_get

        # Get laudes, make sure we have the Notre Pere
        resp = self.app.get('/20/office/laudes/2016-06-8')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: Once, before the Intercession
        self.assertEqual(17, len(items))
        self.assertEqual(u"Oraison et bénédiction", items[-1][0])
        self.assertEqual(u"Notre P&egrave;re", items[-2][0])
        self.assertEqual(u"Intercession", items[-3][0])

