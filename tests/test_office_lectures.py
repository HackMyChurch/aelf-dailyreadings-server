# -*- coding: utf-8 -*-

import mock
from bs4 import BeautifulSoup

from base import TestBase

class TestOfficeLectures(TestBase):
    @mock.patch('utils.requests.Session.get')
    def test_get_lectures_sunday(self, m_get):
        m_get.side_effect = self.m_get

        # Get lectures, make sure we have the Te Deum on a (not so) random sunday
        resp = self.app.get('/20/office/lectures/2017-02-19')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: Once, before the Oraison
        self.assertEqual(14, len(items))
        self.assertEqual(u"Oraison", items[-1][0])
        self.assertEqual(u"Te Deum", items[-2][0])

        self.assertIn(u"Devant toi se prosternent les archanges,", items[-2][1])

    @mock.patch('utils.requests.Session.get')
    def test_get_lectures_other_day(self, m_get):
        m_get.side_effect = self.m_get

        # Get lectures, make sure we have the Te Deum on a (not so) random day
        resp = self.app.get('/20/office/lectures/2017-02-17')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: No Te Deum
        self.assertEqual(13, len(items))
        for item in items:
            self.assertNotEqual(u"Te Deum", item[0])

