import mock

from base import TestBase

class TestOfficeMesses(TestBase):
    @mock.patch('lib.input.requests.Session.get')
    def test_get_holly_saturday_mass(self, m_get):
        m_get.side_effect = self.m_get

        # Get holly saturday
        resp = self.app.get('/76/office/messes/2017-04-15.json')
        self.assertEqual(200, resp.status_code)
        data = resp.json

        # Extract lectures
        self.assertEqual(1, len(data["variants"]))
        lectures = data["variants"][0]["lectures"]
        self.assertEqual(1, len(lectures))

        # Validate: that's not an error, we even go a link
        self.assertEqual("Messe", lectures[0][0]["short_title"])
        self.assertEqual("Le saviez-vous ?", lectures[0][0]["long_title"])
        self.assertIn('http://www.aelf.org/2017-04-16/romain/messe#messe1_lecture1', lectures[0][0]["text"])

    @mock.patch('lib.input.requests.Session.get')
    def test_get_2017_07_29_broken_mass(self, m_get):
        m_get.side_effect = self.m_get

        # Get holly saturday
        resp = self.app.get('/76/office/messes/2017-07-29.json')
        self.assertEqual(200, resp.status_code)
        data = resp.json

        # Extract lectures
        self.assertEqual(1, len(data["variants"]))
        lectures = data["variants"][0]["lectures"]
        self.assertEqual(3, len(lectures))

