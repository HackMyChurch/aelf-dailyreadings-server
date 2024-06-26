import mock
from bs4 import BeautifulSoup

from base import TestBase

class TestOfficeVepres(TestBase):
    @mock.patch('lib.input.requests.Session.get')
    def test_get_vepres(self, m_get):
        m_get.side_effect = self.m_get

        # Get vepres, make sure we have the Notre Pere
        resp = self.app.get('/19/office/vepres/2017-03-02?beta=enabled')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: Once, before the Intercession
        self.assertEqual(16, len(items))
        self.assertEqual("Bénédiction", items[-1][0])
        self.assertEqual("Oraison", items[-2][0])
        self.assertEqual("Notre P&egrave;re", items[-3][0])
        self.assertEqual("Intercession", items[-4][0])

