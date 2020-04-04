# -*- coding: utf-8 -*-

import mock
from bs4 import BeautifulSoup

from base import TestBase

class TestOfficeLaudes(TestBase):
    @mock.patch('lib.input.requests.Session.get')
    def test_get_laudes(self, m_get):
        m_get.side_effect = self.m_get

        # Get laudes, make sure we have the Notre Pere
        resp = self.app.get('/20/office/laudes/2016-06-8')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: Once, before the Intercession
        self.assertEqual(18, len(items))
        self.assertEqual("Bénédiction", items[-1][0])
        self.assertEqual("Oraison", items[-2][0])
        self.assertEqual("Notre P&egrave;re", items[-3][0])
        self.assertEqual("Intercession", items[-4][0])

    @mock.patch('lib.input.requests.Session.get')
    def test_get_laudes_47(self, m_get):
        m_get.side_effect = self.m_get

        # Get laudes, make sure we have the Notre Pere
        resp = self.app.get('/47/office/laudes/2018-01-28')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Basic validation
        self.assertEqual(11, len(items))
        self.assertEqual("Oraison et bénédiction", items[-1][0])
        self.assertEqual("Notre Père", items[-2][0])
        self.assertEqual("Intercession", items[-3][0])

        # Validate 'Antiennes'
        self.assertEqual('Psaume\xa0117', items[3][0])
        self.assertIn('Psaume\xa0117', items[3][1])
        self.assertIn('Antienne', items[3][1])
        self.assertEqual('Cantique des trois enfants', items[4][0])
        self.assertIn('Cantique des trois enfants', items[4][1])
        self.assertIn('Dn 3', items[4][1])
        self.assertNotIn('Antienne', items[4][1])

        # Validate 'Repons'
        self.assertEqual('Parole de Dieu', items[6][0])
        self.assertIn('2 Tm 2, 8.11-13', items[6][1])
        self.assertIn('Il est notre salut, notre gloire éternelle', items[6][1])

