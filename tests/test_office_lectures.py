import mock

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
        self.assertEqual("Oraison", items[-1][0])
        self.assertEqual("Te Deum", items[-2][0])

        self.assertIn("Devant toi se prosternent les archanges,", items[-2][1])

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
            self.assertNotEqual("Te Deum", item[0])

    @mock.patch('lib.input.requests.Session.get')
    def test_get_lectures_47(self, m_get):
        m_get.side_effect = self.m_get

        # Get lectures
        resp = self.app.get('/47/office/lectures/2018-01-28')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate 'Antiennes'
        self.assertEqual('Hymne', items[1][0])
        self.assertIn('«\xa0Voici la nuit\xa0»', items[1][1])
        self.assertNotIn('Antienne', items[1][1])
        self.assertEqual('Psaume\xa023', items[2][0])
        self.assertIn('Psaume\xa023', items[2][1])
        self.assertIn('Antienne', items[2][1])

        # Validate 'Verset'
        self.assertEqual('Psaume\xa065-II', items[4][0])
        self.assertIn('V/', items[4][1])
    
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
