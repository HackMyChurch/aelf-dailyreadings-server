# -*- coding: utf-8 -*-

import mock
from bs4 import BeautifulSoup

from base import TestBase

class TestOfficeLectures(TestBase):
    @mock.patch('utils.requests.get')
    def test_get_lectures_sunday(self, m_get):
        m_get.side_effect = self.m_get

        # Get lectures, make sure we have the Te Deum on a (not so) random sunday
        resp = self.app.get('/20/office/lectures/2016-06-12')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: Once, before the Oraison
        self.assertEqual(15, len(items))
        self.assertEqual(u"Envoi", items[-1][0])
        self.assertEqual(u"Oraison", items[-2][0])
        self.assertEqual(u"Te Deum", items[-3][0])

        self.assertIn(u"Devant toi se prosternent les archanges,", items[-3][1])
        self.assertIn(u"<strong>V/</strong> B\xe9nissons le Seigneur.", items[-1][1])

    @mock.patch('utils.requests.get')
    def test_get_lectures_other_day(self, m_get):
        m_get.side_effect = self.m_get

        # Get lectures, make sure we have the Te Deum on a (not so) random day
        resp = self.app.get('/20/office/lectures/2016-06-11')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: No Te Deum
        self.assertEqual(13, len(items))
        for item in items:
            self.assertNotEqual(u"Te Deum", item[0])

        # Validate: Envoi has the final verse
        self.assertIn(u"<strong>V/</strong> B\xe9nissons le Seigneur.", items[-1][1])

