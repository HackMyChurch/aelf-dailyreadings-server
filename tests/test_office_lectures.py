import mock

from base import TestBase

class TestOfficeLectures(TestBase):
    @mock.patch('lib.input.requests.Session.get')
    def test_get_lectures_sunday(self, m_get):
        m_get.side_effect = self.m_get

        # Get lectures, make sure we have the Te Deum on a (not so) random sunday
        resp = self.app.get('/76/office/lectures/2017-02-19.json')
        self.assertEqual(200, resp.status_code)
        data = resp.json

        # Extract lectures
        self.assertEqual(1, len(data["variants"]))
        lectures = data["variants"][0]["lectures"]
        self.assertEqual(9, len(lectures))

        # Validate: Once, before the Oraison
        self.assertEqual("Oraison", lectures[-1][0]["short_title"])
        self.assertEqual("Te Deum", lectures[-2][0]["short_title"])

        self.assertIn("Devant toi se prosternent les archanges,", lectures[-2][0]["text"])

    @mock.patch('lib.input.requests.Session.get')
    def test_get_lectures_other_day(self, m_get):
        m_get.side_effect = self.m_get

        # Get lectures, make sure we have the Te Deum on a (not so) random day
        resp = self.app.get('/76/office/lectures/2017-02-17.json')
        self.assertEqual(200, resp.status_code)
        data = resp.json

        # Extract lectures
        self.assertEqual(1, len(data["variants"]))
        lectures = data["variants"][0]["lectures"]
        self.assertEqual(8, len(lectures))

        # Validate: No Te Deum
        for lecture in lectures:
            self.assertNotEqual("Te Deum", lecture[0]["short_title"])

    @mock.patch('lib.input.requests.Session.get')
    def test_get_lectures(self, m_get):
        m_get.side_effect = self.m_get

        # Get lectures
        resp = self.app.get('/76/office/lectures/2018-01-28.json')
        self.assertEqual(200, resp.status_code)
        data = resp.json

        # Extract lectures
        self.assertEqual(1, len(data["variants"]))
        lectures = data["variants"][0]["lectures"]
        self.assertEqual(9, len(lectures))

        # Validate 'Antiennes'
        self.assertEqual('Hymne', lectures[1][0]["short_title"])
        self.assertEqual('«\xa0Voici la nuit\xa0»', lectures[1][0]["long_title"])
        self.assertNotIn('antienne', lectures[1][0])
        self.assertEqual("Psaume\xa023", lectures[2][0]["long_title"])
        self.assertIn('antienne', lectures[2][0])

        # Validate 'Verset'
        self.assertEqual('Psaume\xa065-II', lectures[4][0]["short_title"])
        self.assertIn('V/', lectures[4][0]["verset"])
    
    @mock.patch('lib.input.requests.Session.get')
    def test_get_lectures_copyright(self, m_get):
        m_get.side_effect = self.m_get

        # Get lectures
        resp = self.app.get('/76/office/lectures/2024-05-21.json')
        self.assertEqual(200, resp.status_code)
        office = resp.json

        # Check the copyright on the hymn
        lecture_hymn = office["variants"][0]["lectures"][1][0]
        self.assertEqual("CFC", lecture_hymn['author'])
        self.assertEqual("CNPL", lecture_hymn['editor'])
        self.assertEqual("CFC, CNPL", lecture_hymn['reference'])
