import mock

from base import TestBase

class TestOfficeLaudes(TestBase):
    @mock.patch('lib.input.requests.Session.get')
    def test_get_holly_saturday_mass(self, m_get):
        m_get.side_effect = self.m_get

        # Get holly saturday
        resp = self.app.get('/29/office/messes/2017-04-15')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: that's not an error, we even go a link
        self.assertEqual(1, len(items))
        self.assertEqual("Messe: Le saviez-vous ?", items[0][0])
        self.assertIn('http://www.aelf.org/2017-04-16/romain/messe#messe1_lecture1', items[0][1])

    @mock.patch('lib.input.requests.Session.get')
    def test_get_2017_07_29_broken_mass(self, m_get):
        m_get.side_effect = self.m_get

        # Get holly saturday
        resp = self.app.get('/29/office/messes/2017-07-29')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: we get 3 lectures
        self.assertEqual(3, len(items))

