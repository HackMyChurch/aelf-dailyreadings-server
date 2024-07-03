import mock

from base import TestBase

class TestOfficeLaudes(TestBase):
    @mock.patch('lib.input.requests.Session.get')
    def test_get_laudes(self, m_get):
        m_get.side_effect = self.m_get

        # Get laudes, make sure we have the Notre Pere
        resp = self.app.get('/76/office/laudes/2018-01-28.json')
        self.assertEqual(200, resp.status_code)
        data = resp.json

        # Extract lectures
        self.assertEqual(1, len(data["variants"]))
        lectures = data["variants"][0]["lectures"]
        self.assertEqual(11, len(lectures))

        # Basic validation
        self.assertEqual("Oraison et bénédiction", lectures[-1][0]["short_title"])
        self.assertEqual("Notre Père", lectures[-2][0]["short_title"])
        self.assertEqual("Intercession", lectures[-3][0]["short_title"])

        # Validate alternative psaume invitatoires
        self.assertEqual(4, len(lectures[1]))
        self.assertEqual('Ps 94', lectures[1][0]['reference'])
        self.assertEqual('Ps 66', lectures[1][1]['reference'])
        self.assertEqual('Ps 99', lectures[1][2]['reference'])
        self.assertEqual('Ps 23', lectures[1][3]['reference'])

        # Validate 'Antiennes'
        self.assertEqual('Psaume\xa0117', lectures[3][0]["short_title"])
        self.assertIn('antienne', lectures[3][0])
        self.assertEqual('Cantique des trois enfants', lectures[4][0]["short_title"])
        self.assertIn('Cantique des trois enfants', lectures[4][0]["long_title"])
        self.assertIn('Dn 3', lectures[4][0]["reference"])
        self.assertNotIn('antienne', lectures[4][0])

        # Validate 'Repons'
        self.assertEqual('Parole de Dieu', lectures[6][0]["short_title"])
        self.assertIn('2 Tm 2, 8.11-13', lectures[6][0]["reference"])
        self.assertIn('Il est notre salut, notre gloire éternelle', lectures[6][0]["repons"])

        # Validate end
        self.assertEqual("Notre Père", lectures[-2][0]["short_title"])
        self.assertEqual("Intercession", lectures[-3][0]["short_title"])

