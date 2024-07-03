import mock

from base import TestBase

class TestOfficeComplies(TestBase):
    @mock.patch('lib.input.requests.Session.get')
    def test_get_complies(self, m_get):
        m_get.side_effect = self.m_get

        # Get vepres, make sure we have the Notre Pere
        resp = self.app.get('/76/office/complies/2017-02-19.json')
        self.assertEqual(200, resp.status_code)
        data = resp.json

        # Extract lectures
        self.assertEqual(1, len(data['variants']))
        lectures = data["variants"][0]['lectures']
        self.assertEqual(7, len(lectures))

        # Validate: Once, before the Intercession
        self.assertEqual("Nous te saluons, Vierge Marie", lectures[-1][0]["short_title"])
        self.assertEqual("Oraison et bénédiction", lectures[-2][0]["short_title"])
        self.assertIn(
            "Que le Seigneur nous bénisse et nous garde",
            lectures[-2][0]['text'].replace("\r\n", ""),
        )
        self.assertIn(
            "Notre Seigneur et notre Dieu, tu nous as fait entendre ton amour au matin de la Résurrection",
            lectures[-2][0]['text'].replace("\r\n", ""),
        )

        # Validate: alléluia
        self.assertEqual("Introduction", lectures[0][0]["short_title"])
        self.assertIn("alléluia", lectures[0][0]["text"].lower())

    @mock.patch('lib.input.requests.Session.get')
    def test_no_alleluia_careme(self, m_get):
        m_get.side_effect = self.m_get

        # Get vepres, make sure we have the Notre Pere
        resp = self.app.get('/76/office/complies/2017-03-05.json')
        self.assertEqual(200, resp.status_code)
        data = resp.json

        # Extract lectures
        self.assertEqual(1, len(data['variants']))
        lectures = data["variants"][0]['lectures']
        self.assertEqual(7, len(lectures))

        # Validate: no alléluia
        self.assertEqual("Introduction", lectures[0][0]["short_title"])
        self.assertNotIn("alléluia",     lectures[0][0]["text"].lower())

