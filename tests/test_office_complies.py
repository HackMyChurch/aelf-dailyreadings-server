import mock

from base import TestBase

class TestOfficeComplies(TestBase):
    @mock.patch('lib.input.requests.Session.get')
    def test_get_complies(self, m_get):
        m_get.side_effect = self.m_get

        # Get vepres, make sure we have the Notre Pere
        resp = self.app.get('/28/office/complies/2017-02-19?beta=enabled')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: Once, before the Intercession
        self.assertEqual(12, len(items))
        self.assertEqual("Nous te saluons, Vierge Marie", items[-1][0])
        self.assertEqual("Bénédiction", items[-2][0])
        self.assertEqual("Oraison", items[-3][0])
        self.assertEqual(
            "Que le Seigneur nous b\xe9nisse et nous garde,<br />le P\xe8re, le Fils, et le Saint-Esprit. Amen.",
            items[-2][1].replace('\r\n', '')
        )
        self.assertEqual(
            "Notre Seigneur et notre Dieu, tu nous as fait entendre ton amour au matin de la R\xe9surrection ; quand viendra pour nous le moment de mourir, que ton souffle de vie nous conduise en ta pr\xe9sence. Par J\xe9sus, le Christ, notre Seigneur. Amen.",
            items[-3][1]
        )

        # Validate: no alléluia
        self.assertEqual("Introduction", items[0][0])
        self.assertIn('alléluia',        items[0][1].lower())

    @mock.patch('lib.input.requests.Session.get')
    def test_no_alleluia_careme(self, m_get):
        m_get.side_effect = self.m_get

        # Get vepres, make sure we have the Notre Pere
        resp = self.app.get('/28/office/complies/2017-03-05')
        self.assertEqual(200, resp.status_code)
        items = self.parseItems(resp.data)

        # Validate: no alléluia
        self.assertEqual(12, len(items))
        self.assertEqual("Introduction", items[0][0])
        self.assertNotIn('alléluia',     items[0][1].lower())

