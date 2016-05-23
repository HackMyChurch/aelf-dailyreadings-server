# -*- coding: utf-8 -*-

import mock
from bs4 import BeautifulSoup

from base import TestBase

class TestOfficeComplies(TestBase):
    @mock.patch('utils.requests.get')
    def test_get_complies(self, m_get):
        m_get.side_effect = self.m_get

        # Get vepres, make sure we have the Notre Pere
        resp = self.app.get('/19/office/complies/2016-05-23?beta=enabled')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: Once, before the Intercession
        self.assertEqual(13, len(items))
        self.assertEqual(u"Hymne Salut, Reine des cieux ! Salut, Reine des anges !", items[-1][0])
        self.assertEqual(u"Bénédiction", items[-2][0])
        self.assertEqual(u"Oraison", items[-3][0])

