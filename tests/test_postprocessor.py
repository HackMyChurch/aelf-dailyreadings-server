# -*- coding: utf-8 -*-

import unittest
from bs4 import BeautifulSoup

# verse number
# paragraphs
# intercession
# lines
# tipography
# font --> remove size
# font --> keep red / normalize
# font --> remove any other color (black...)
# inflexion (*+) --> <sup>

def t2bs(data): return BeautifulSoup(data, 'html5lib')
def bs2t(data): return unicode(data.body)[6:-7]
def bs(func, data, *args, **kwargs):
    soup = t2bs(data)
    func(soup, *args, **kwargs)
    return bs2t(soup)

class TestPostprocessor(unittest.TestCase):
    def test__is_verse_ref(self):
        from lib.postprocessor import _is_verse_ref

        self.assertTrue(_is_verse_ref('1'))
        self.assertTrue(_is_verse_ref('1A'))
        self.assertTrue(_is_verse_ref('1.42'))

        self.assertFalse(_is_verse_ref('1a'))
        self.assertFalse(_is_verse_ref('1.'))
        self.assertFalse(_is_verse_ref('1.42a'))

    def test_html_fix_font(self):
        from lib.postprocessor import html_fix_font

        # Noop
        self.assertEqual("", bs(html_fix_font, ""))
        self.assertEqual("<p>hello</p>", bs(html_fix_font, "<p>hello</p>"))

        # Non-red
        self.assertEqual("hello", bs(html_fix_font, "<font>hello</font>"))
        self.assertEqual("hello", bs(html_fix_font, "<font color='#'>hello</font>"))
        self.assertEqual("hello", bs(html_fix_font, "<font color='#0'>hello</font>"))
        self.assertEqual("hello", bs(html_fix_font, "<font color='#0'>hello</font>"))
        self.assertEqual("hello", bs(html_fix_font, "<font color='#000'>hello</font>"))
        self.assertEqual("hello", bs(html_fix_font, "<font color='#000000'>hello</font>"))
        self.assertEqual("hello", bs(html_fix_font, "<font color='#fff'>hello</font>"))

        # Red, text
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_font, '<font color="#Ff0000">hello</font>'))
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_font, '<font color="#cC0000">hello</font>'))
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_font, '<font color="#f00">hello</font>'))
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_font, '<font color="#c00">hello</font>'))
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_font, '<font color="#c00" some_tag="data">hello</font>'))

        # Red, verse
        self.assertEqual('<span aria-hidden="true" class="verse verse-v2">1.42</span>', bs(html_fix_font, '<font color="#f00"> 1.42 </font>'))

    def test_fix_case(self):
        from lib.postprocessor import fix_case

        self.assertEqual(u'Homelie d\'Origène sur le Lévitique', fix_case(u'HOMELIE D\'ORIGÈNE SUR LE LÉVITIQUE'))
        self.assertEqual(u'Sermon de saint L\xe9on le grand Pour l\'anniversaire de son ordination', fix_case(u'SERMON DE S. LÉON LE GRAND POUR L\'ANNIVERSAIRE DE SON ORDINATION'))
