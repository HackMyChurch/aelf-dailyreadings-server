# -*- coding: utf-8 -*-

import mock

from base import TestBase

class TestOfficeMeta(TestBase):
    def assertMetaEqual(self, date, meta):
        resp = self.app.get('/19/office/meta/%s?beta=enabled' % date)
        self.assertEqual(200, resp.status_code)
        return self.assertItemsEqual([(u"Jour liturgique", meta)], resp.data)

    @mock.patch('utils.requests.Session.get')
    def test_get_meta(self, m_get):
        m_get.side_effect = self.m_get
        self.maxDiff = None

        # Nominal tests
        self.assertMetaEqual("2015-12-25", u"Année A. Nous célèbrons la Nativité du Seigneur. La couleur liturgique est le Blanc.")
        self.assertMetaEqual("2016-03-27", u"Dimanche de l'année C. Nous célèbrons la Résurrection du Seigneur. La couleur liturgique est le Blanc.")
        self.assertMetaEqual("2016-05-08", u"Dimanche, 7<sup>ème</sup> Semaine du Temps Pascal (semaine III du psautier) de l'année C. La couleur liturgique est le Blanc.")
        self.assertMetaEqual("2016-05-15", u"Dimanche de la Pentecôte, année C. La couleur liturgique est le Rouge.")
        self.assertMetaEqual("2016-05-25", u"Mercredi, 8<sup>ème</sup> Semaine du Temps Ordinaire (semaine IV du psautier) de l'année Paire. Nous fêtons Saint Bède le Vénérable, prêtre et docteur de l'Eglise, Saint Grégoire VII, pape, Sainte Marie-Madeleine de Pazzi, vierge. La couleur liturgique est le Vert.")
        self.assertMetaEqual("2016-06-05", u"Dimanche, 10<sup>ème</sup> Semaine du Temps Ordinaire (semaine II du psautier) de l'année C. La couleur liturgique est le Vert.")
        self.assertMetaEqual("2016-06-03", u"Vendredi de l'année C. Nous célèbrons le Sacré-C\u0153ur de Jésus. La couleur liturgique est le Blanc.")
        self.assertMetaEqual("2016-06-11", u"Samedi, 10<sup>ème</sup> Semaine du Temps Ordinaire (semaine II du psautier) de l'année Paire. Nous fêtons Saint Barnabé. La couleur liturgique est le Rouge.")
        self.assertMetaEqual("2016-08-15", u"Nous célèbrons l'Assomption de la Vierge Marie. La couleur liturgique est le Blanc.")

        # Error: obviously invalid date
        resp = self.app.get('/0/office/meta/2016-42')
        self.assertEqual(400, resp.status_code)
        resp = self.app.get('/0/office/meta/2016-42-17')
        self.assertItemsEqual([(u"Ooops... Cette lecture n'est pas dans notre calendrier (404)", u"<p>Saviez-vous que cette application est d\xe9velopp\xe9e compl\xe8tement b\xe9n\xe9volement&nbsp;? Elle est construite en lien et avec le soutien de l\'AELF, mais elle reste un projet ind\xe9pendant, soutenue par <em>votre</em> pri\xe8re&nbsp!</p>\n<p>Si vous pensez qu\'il s\'agit d\'une erreur, vous pouvez envoyer un mail \xe0 <a href=\"mailto:cathogeek@epitre.co\">cathogeek@epitre.co</a>.<p>")], resp.data)

