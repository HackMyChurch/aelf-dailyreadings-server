# -*- coding: utf-8 -*-

import unittest

class TestPostprocessor(unittest.TestCase):
    def test_fix_case(self):
        from lib.postprocessor import fix_case

        self.assertEqual(u'Homelie d\'Origène sur le Lévitique', fix_case(u'HOMELIE D\'ORIGÈNE SUR LE LÉVITIQUE'))
        self.assertEqual(u'Sermon de saint L\xe9on le grand Pour l\'anniversaire de son ordination', fix_case(u'SERMON DE S. LÉON LE GRAND POUR L\'ANNIVERSAIRE DE SON ORDINATION'))
