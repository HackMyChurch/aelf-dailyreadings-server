# -*- coding: utf-8 -*-

import unittest
from bs4 import BeautifulSoup

# verse number
# paragraphs
# intercession
# lines
# tipography
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

    def test_html_fix_comments(self):
        from lib.postprocessor import html_fix_comments

        # Nominal
        self.assertEqual("", bs(html_fix_comments, ""))
        self.assertEqual("<p>hello</p>", bs(html_fix_comments, "<p>hello</p>"))
        self.assertEqual("<p>hello</p>", bs(html_fix_comments, "<p>hello<!-- comment --></p>"))
        self.assertEqual("<p>hello</p>", bs(html_fix_comments, "<p>hello<!-- comment --></p><!-- <u>test</u> -->"))

    def test_html_fix_verse(self):
        from lib.postprocessor import html_fix_verse

        # Noop
        self.assertEqual("", bs(html_fix_verse, ""))
        self.assertEqual("<p>hello</p>", bs(html_fix_verse, "<p>hello</p>"))

        # Non-red
        self.assertEqual("hello", bs(html_fix_verse, "<font>hello</font>"))
        self.assertEqual("hello", bs(html_fix_verse, "<font color='#'>hello</font>"))
        self.assertEqual("hello", bs(html_fix_verse, "<font color='#0'>hello</font>"))
        self.assertEqual("hello", bs(html_fix_verse, "<font color='#0'>hello</font>"))
        self.assertEqual("hello", bs(html_fix_verse, "<font color='#000'>hello</font>"))
        self.assertEqual("hello", bs(html_fix_verse, "<font color='#000000'>hello</font>"))
        self.assertEqual("hello", bs(html_fix_verse, "<font color='#fff'>hello</font>"))

        # Red, text
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_verse, '<font color="#Ff0000">hello</font>'))
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_verse, '<font color="#cC0000">hello</font>'))
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_verse, '<font color="#f00">hello</font>'))
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_verse, '<font color="#c00">hello</font>'))
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_verse, '<font color="#c00" some_tag="data">hello</font>'))

        # Red, verse
        self.assertEqual('<span aria-hidden="true" class="verse verse-v2">1.42</span>', bs(html_fix_verse, '<font color="#f00"> 1.42 </font>'))

        # Pre-existing verse
        self.assertEqual('<span aria-hidden="true" class="verse verse-v2">42</span>', bs(html_fix_verse, '<span class="verse_number" disabled="true">42</span>'))

    def test_html_fix_paragraph(self):
        from lib.postprocessor import html_fix_paragraph

        # Noop
        self.assertEqual('',                                  bs(html_fix_paragraph, ''))
        self.assertEqual('<p>hello</p><p>world</p>',          bs(html_fix_paragraph, '<p>hello</p><p>world</p>'))
        self.assertEqual('<p>hello</p><p>nice<br/>world</p>', bs(html_fix_paragraph, '<p>hello</p><p>nice<br/>world</p>'))

        # Simple paragraph wrap
        self.assertEqual('', bs(html_fix_paragraph, '<br>'))
        self.assertEqual('<p><br/>hello</p>', bs(html_fix_paragraph, '<br>hello'))
        self.assertEqual('<p><br/>world</p>', bs(html_fix_paragraph, '<br/>world'))

        # Trim empty p
        self.assertEqual('<p>Hello</p>', bs(html_fix_paragraph, '<p></p><p>Hello</p>'))

        # Paragraph reconstruction and cleanup
        self.assertEqual('<p>hello<br/>world</p>',              bs(html_fix_paragraph, 'hello<br/>world'))
        self.assertEqual('<p>hello</p><p>nice</p><p>world</p>', bs(html_fix_paragraph, 'hello<br/><br><br/>nice<br/><br/><br/>world'))
        self.assertEqual('<p>hello<br/>nice</p><p>world</p>',   bs(html_fix_paragraph, 'hello<br/>nice<br/><br/><br/>world'))
        self.assertEqual('<p>hello world</p>',                  bs(html_fix_paragraph, 'hello world<br/><br/>'))

        # Paragraph cleaner
        self.assertEqual('<p>world</p>', bs(html_fix_paragraph, '<p style="text-decoration: underline;" class="hello">world</p>'))

    def test_html_fix_lines(self):
        from lib.postprocessor import html_fix_lines

        # Noop
        self.assertEqual('', bs(html_fix_lines, ''))
        self.assertEqual('<p><line class="wrap">hello</line><line class="wrap">world</line></p>',        bs(html_fix_lines, '<p><line class="wrap">hello</line><line class="wrap">world</line></p>'))
        self.assertEqual('<p><line class="wrap">hello</line></p><p><line class="wrap">world</line></p>', bs(html_fix_lines, '<p><line class="wrap">hello</line></p><p><line class="wrap">world</line></p>'))

        # Simple line wrap
        self.assertEqual('<p><line class="wrap">hello world</line></p>', bs(html_fix_lines, '<p>hello world</p>'))

        # Nested line wrap
        self.assertEqual('<p><line class="wrap"><strong>hello</strong></line><line class="wrap"><strong>world</strong></line></p>', bs(html_fix_lines, '<p><strong>hello<br/>world</strong></p>'))

        # Trim empty line
        self.assertEqual('<p><line class="wrap">Hello</line></p>', bs(html_fix_lines, '<p><br/>Hello</p>'))

        # Line reconstruction
        self.assertEqual('<p><line class="wrap">hello</line><line class="wrap">world</line></p><p><line class="wrap">hello</line><line class="wrap">world</line></p>', bs(html_fix_lines, '<p>hello<br/>world</p><p>hello<br/>world</p>'))
        self.assertEqual('<p><line class="wrap">aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</line></p>', bs(html_fix_lines, '<p>aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</p>'))
        self.assertEqual('<p><line>aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</line></p>', bs(html_fix_lines, '<p>aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</p>'))
        self.assertEqual('<p><line class="wrap">hello world</line></p>', bs(html_fix_lines, '<p><br/>hello world</p>'))

    def test_fix_common_typography(self):
        from lib.postprocessor import fix_common_typography

        # Nominal
        self.assertEqual(u'',      fix_common_typography(u''))
        self.assertEqual(u'Père',  fix_common_typography(u'Pere'))
        self.assertEqual(u'père',  fix_common_typography(u'pere'))
        self.assertEqual(u'degré', fix_common_typography(u'degre'))
        self.assertEqual(u'cœur',  fix_common_typography(u'coeur'))
        self.assertEqual(u'cœur',  fix_common_typography(u'coeur'))

	# Typography
        self.assertEqual(u'\xa0', fix_common_typography(u'&nbsp;'))
        self.assertEqual(u'\xa0;', fix_common_typography(u'&nbsp;;'))
        self.assertEqual(u'\xa0;', fix_common_typography(u'&nbsp; ;'))
        self.assertEqual(u'Hello world\xa0! ', fix_common_typography(u'Hello world!'))
        self.assertEqual(u' «\xa0Hello World\xa0» ', fix_common_typography(u'«Hello World»'))
        self.assertEqual(u' «\xa0Hello World\xa0» ', fix_common_typography(u'&laquo;Hello World&raquo;'))

    def test_fix_case(self):
        from lib.postprocessor import fix_case

        self.assertEqual(u'Homelie d\'Origène sur le Lévitique', fix_case(u'HOMELIE D\'ORIGÈNE SUR LE LÉVITIQUE'))
        self.assertEqual(u'Sermon de saint L\xe9on le grand pour l\'anniversaire de son ordination', fix_case(u'SERMON DE S. LÉON LE GRAND POUR L\'ANNIVERSAIRE DE SON ORDINATION'))
        self.assertEqual(u'Actes du Concile Vatican II', fix_case(u'Actes Du Concile Vatican ii'))
        self.assertEqual(u'Psaume IV', fix_case(u'pSauMe iv'))
