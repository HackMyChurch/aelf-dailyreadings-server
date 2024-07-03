import mock

from base import TestBase, FakeResponse

class TestOfficeMeta(TestBase):
    def tearDown(self):
        FakeResponse.status_code = 200

    def assertMetaEqual(self, date, expected_text):
        resp = self.app.get(f'/76/office/informations/{date}.json')
        self.assertEqual(200, resp.status_code)
        data = resp.json

        self.assertEqual(1, len(data["variants"]))
        self.assertEqual(1, len(data["variants"][0]["lectures"]))
        self.assertEqual(1, len(data["variants"][0]["lectures"][0]))

        self.assertEqual(
            expected_text,
            data["variants"][0]["lectures"][0][0]["text"],
        )

    @mock.patch('lib.input.requests.Session.get')
    def test_get_meta(self, m_get):
        m_get.side_effect = self.m_get
        self.maxDiff = None

        # Nominal tests
        self.assertMetaEqual("2016-12-25", "Nous c\xe9l\xe8brons la Nativit\xe9 du Seigneur de l'ann\xe9e A. La couleur liturgique est le blanc.")
        self.assertMetaEqual("2017-03-16", "Jeudi de la f\xe9rie, 2<sup>\xe8me</sup> Semaine de Car\xeame (semaine II du psautier). La couleur liturgique est le violet.")
        self.assertMetaEqual("2017-04-16", "Nous c\xe9l\xe8brons la R\xe9surrection du Seigneur de l'ann\xe9e A. La couleur liturgique est le blanc.")
        self.assertMetaEqual("2017-05-28", "Dimanche, 7<sup>ème</sup> Semaine du Temps Pascal (semaine III du psautier) de l'année A. La couleur liturgique est le blanc.")
        self.assertMetaEqual("2017-06-04", "Nous c\xe9l\xe8brons la Pentec\xf4te de l'ann\xe9e A. La couleur liturgique est le rouge.")
        self.assertMetaEqual("2017-05-12", "Vendredi de la f\xe9rie, 4<sup>\xe8me</sup> Semaine du Temps Pascal (semaine IV du psautier). Nous f\xeatons saint N\xe9r\xe9e et saint Achille, martyrs ; saint Pancrace, martyr. La couleur liturgique est le blanc.")
        self.assertMetaEqual("2017-05-19", "Vendredi de la f\xe9rie, 5<sup>\xe8me</sup> Semaine du Temps Pascal (semaine I du psautier). Nous f\xeatons saint Yves. La couleur liturgique est le blanc.")
        self.assertMetaEqual("2017-05-25", "Jeudi. Nous c\xe9l\xe8brons l'Ascension. La couleur liturgique est le blanc.")
        self.assertMetaEqual("2016-06-11", "Samedi de la f\xe9rie, 10<sup>\xe8me</sup> Semaine du Temps Ordinaire (semaine II du psautier) de l'ann\xe9e Paire. Nous f\xeatons saint Barnab\xe9. La couleur liturgique est le rouge.")
        self.assertMetaEqual("2016-06-12", "Dimanche, 11<sup>ème</sup> Semaine du Temps Ordinaire (semaine III du psautier) de l'année C. La couleur liturgique est le vert.")
        self.assertMetaEqual("2016-08-15", "Nous célèbrons l'Assomption de la Vierge Marie. La couleur liturgique est le blanc.")
