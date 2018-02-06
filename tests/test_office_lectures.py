# -*- coding: utf-8 -*-

import mock
from bs4 import BeautifulSoup

from base import TestBase

class TestOfficeLectures(TestBase):
    @mock.patch('lib.input.requests.Session.get')
    def test_get_lectures_sunday(self, m_get):
        m_get.side_effect = self.m_get

        # Get lectures, make sure we have the Te Deum on a (not so) random sunday
        resp = self.app.get('/20/office/lectures/2017-02-19')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: Once, before the Oraison
        self.assertEqual(15, len(items))
        self.assertEqual(u"Oraison", items[-1][0])
        self.assertEqual(u"Te Deum", items[-2][0])

        self.assertIn(u"Devant toi se prosternent les archanges,", items[-2][1])

    @mock.patch('lib.input.requests.Session.get')
    def test_get_lectures_other_day(self, m_get):
        m_get.side_effect = self.m_get

        # Get lectures, make sure we have the Te Deum on a (not so) random day
        resp = self.app.get('/20/office/lectures/2017-02-17')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: No Te Deum
        self.assertEqual(14, len(items))
        for item in items:
            self.assertNotEqual(u"Te Deum", item[0])

    @mock.patch('lib.input.requests.Session.get')
    def test_get_lectures_fallback_missing_lecture(self, m_get):
        m_get.side_effect = self.m_get

        # Get lectures, make sure we have the Te Deum on a (not so) random day
        resp = self.app.get('/20/office/lectures/2017-03-03')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: No Te Deum
        self.assertEqual(14, len(items))
        for item in items:
            self.assertNotEqual(u"Te Deum", item[0])

        # Has a valid lecture
        self.assertEqual(u"Lecture : Mo\xefse, le d\xe9fenseur des H\xe9breux pers\xe9cut\xe9s  (Exode 2, 1 - 22)", items[-5][0])
        self.assertIn(u"Voyant qu\u2019il \xe9tait beau", items[-5][1])

    @mock.patch('lib.input.requests.Session.get')
    def test_get_lectures_47(self, m_get):
        m_get.side_effect = self.m_get

        # Get laudes, make sure we have the Notre Pere
        resp = self.app.get('/47/office/lectures/2018-01-28')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate 'Antiennes'
        self.assertEqual(u'Hymne', items[1][0])
        self.assertIn(u'«\xa0Voici la nuit\xa0»', items[1][1])
        self.assertNotIn(u'Antienne', items[1][1])
        self.assertEqual(u'Psaume\xa023', items[2][0])
        self.assertIn(u'Psaume\xa023', items[2][1])
        self.assertIn(u'Antienne', items[2][1])

        # Validate 'Verset'
        self.assertEqual(u'Psaume\xa065-II', items[4][0])
        self.assertIn(u'V/', items[4][1])

