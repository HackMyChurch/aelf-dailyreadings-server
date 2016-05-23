# -*- coding: utf-8 -*-

import mock
from bs4 import BeautifulSoup

from base import TestBase

class TestOfficeMeta(TestBase):
    @mock.patch('utils.requests.get')
    def test_get_vepres(self, m_get):
        m_get.side_effect = self.m_get

        # Get vepres, make sure we have the Notre Pere
        resp = self.app.get('/19/office/vepres/2016-05-23?beta=enabled')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: Once, before the Intercession
        self.assertEqual(14, len(items))
        self.assertEqual(u"Oraison et bénédiction", items[-1][0])
        self.assertEqual(u"Notre P&egrave;re", items[-2][0])
        self.assertEqual(u"Intercession", items[-3][0])

