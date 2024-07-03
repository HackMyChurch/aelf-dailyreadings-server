import mock

from base import TestBase

class TestOfficeVepres(TestBase):
    @mock.patch('lib.input.requests.Session.get')
    def test_get_vepres(self, m_get):
        m_get.side_effect = self.m_get

        # Get vepres, make sure we have the Notre Pere
        resp = self.app.get('/76/office/vepres/2017-03-02.json')
        self.assertEqual(200, resp.status_code)
        data = resp.json

        # Extract lectures
        self.assertEqual(1, len(data["variants"]))
        lectures = data["variants"][0]["lectures"]
        self.assertEqual(10, len(lectures))

        # Validate: Once, before the Intercession
        self.assertEqual("Oraison et bénédiction", lectures[-1][0]["short_title"])
        self.assertEqual("Notre Père", lectures[-2][0]["short_title"])
        self.assertEqual("Intercession", lectures[-3][0]["short_title"])

