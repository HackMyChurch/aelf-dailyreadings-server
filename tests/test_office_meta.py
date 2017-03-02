# -*- coding: utf-8 -*-

import mock

from base import TestBase, FakeResponse

class TestOfficeMeta(TestBase):
    def tearDown(self):
        FakeResponse.status_code = 200

    def assertMetaEqual(self, date, meta):
        resp = self.app.get('/19/office/informations/%s?beta=enabled' % date)
        self.assertEqual(200, resp.status_code)
        return self.assertItemsEqual([(u"Jour liturgique", meta)], resp.data)

    @mock.patch('utils.requests.Session.get')
    def test_get_meta(self, m_get):
        m_get.side_effect = self.m_get
        self.maxDiff = None

        # Nominal tests
        self.assertMetaEqual("2016-12-25", u"Nous c\xe9l\xe8brons la Nativit\xe9 du Seigneur de l'ann\xe9e A. La couleur liturgique est le blanc.")
        self.assertMetaEqual("2017-03-16", u"Jeudi de la f\xe9rie, 2<sup>\xe8me</sup> Semaine de Car\xeame (semaine II du psautier). La couleur liturgique est le violet.")
        self.assertMetaEqual("2017-04-16", u"Nous c\xe9l\xe8brons la R\xe9surrection du Seigneur de l'ann\xe9e A. La couleur liturgique est le blanc.")
        self.assertMetaEqual("2017-05-28", u"Dimanche, 7<sup>ème</sup> Semaine du Temps Pascal (semaine III du psautier) de l'année A. La couleur liturgique est le blanc.")
        self.assertMetaEqual("2017-06-04", u"Nous c\xe9l\xe8brons la Pentec\xf4te de l'ann\xe9e A. La couleur liturgique est le rouge.")
        self.assertMetaEqual("2017-05-12", u"Vendredi de la f\xe9rie, 4<sup>\xe8me</sup> Semaine du Temps Pascal (semaine IV du psautier). Nous f\xeatons Saint N\xe9r\xe9e et Saint Achille, martyrs ; Saint Pancrace, martyr. La couleur liturgique est le blanc.")
        self.assertMetaEqual("2017-05-19", u"Vendredi de la f\xe9rie, 5<sup>\xe8me</sup> Semaine du Temps Pascal (semaine I du psautier). Nous f\xeatons Saint Yves. La couleur liturgique est le blanc.")
        self.assertMetaEqual("2017-05-25", u"Jeudi. Nous c\xe9l\xe8brons l'Ascension. La couleur liturgique est le blanc.")
        self.assertMetaEqual("2016-06-11", u"Samedi de la f\xe9rie, 10<sup>\xe8me</sup> Semaine du Temps Ordinaire (semaine II du psautier) de l'ann\xe9e Paire. Nous f\xeatons Saint Barnab\xe9. La couleur liturgique est le rouge.")
        self.assertMetaEqual("2016-06-12", u"Dimanche, 11<sup>ème</sup> Semaine du Temps Ordinaire (semaine III du psautier) de l'année C. La couleur liturgique est le vert.")
        self.assertMetaEqual("2016-08-15", u"Nous célèbrons l'Assomption de la Vierge Marie. La couleur liturgique est le blanc.")

        # Error: obviously invalid date
        FakeResponse.status_code = 404
        resp = self.app.get('/0/office/meta/2016-42')
        self.assertEqual(400, resp.status_code)
        resp = self.app.get('/0/office/informations/2016-42-17')
        self.assertItemsEqual([(u"Oups... Cette lecture n'est pas dans notre calendrier (404)", u'<p>Aucune lecture n\'a \xe9t\xe9 trouv\xe9e pour cette date.</p>\n<p>Saviez-vous que cette application est d\xe9velopp\xe9e compl\xe8tement b\xe9n\xe9volement&nbsp;? Elle est construite en lien et avec le soutien de l\'AELF, mais elle reste un projet ind\xe9pendant, soutenue par <em>votre</em> pri\xe8re&nbsp!</p>\n<p>Si vous pensez qu\'il s\'agit d\'une erreur, vous pouvez envoyer un mail \xe0 <a href="mailto:cathogeek@epitre.co">cathogeek@epitre.co</a>.<p>')], resp.data)

