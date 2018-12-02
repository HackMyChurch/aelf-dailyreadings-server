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
    func("test-key", soup, *args, **kwargs)
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
        self.assertEqual("<p>hello<font color=\"#CC0000\">R/ </font></p>", bs(html_fix_comments, """<p>hello<font color="#CC0000">R/ <!--[if gte mso 9]><xml>
        <o:OfficeDocumentSettings>
            <o:TargetScreenSize>800x600</o:TargetScreenSize>
        </o:OfficeDocumentSettings>
        </xml><![endif]--></font></p>"""))

    def test_html_fix_verse(self):
        from lib.postprocessor import html_fix_verse

        # Noop
        self.assertEqual("", bs(html_fix_verse, ""))
        self.assertEqual("<p>hello</p>", bs(html_fix_verse, "<p>hello</p>"))

        # Non-red (FIXME: it should drop the 'font' tag BUT that causes some crashes. See code for more info)
        self.assertEqual("<font>hello</font>", bs(html_fix_verse, "<font>hello</font>"))
        self.assertEqual("<font>hello</font>", bs(html_fix_verse, "<font color='#'>hello</font>"))
        self.assertEqual("<font>hello</font>", bs(html_fix_verse, "<font color='#0'>hello</font>"))
        self.assertEqual("<font>hello</font>", bs(html_fix_verse, "<font color='#0'>hello</font>"))
        self.assertEqual("<font>hello</font>", bs(html_fix_verse, "<font color='#000'>hello</font>"))
        self.assertEqual("<font>hello</font>", bs(html_fix_verse, "<font color='#000000'>hello</font>"))
        self.assertEqual("<font>hello</font>", bs(html_fix_verse, "<font color='#fff'>hello</font>"))

        # Red, text
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_verse, '<font color="#Ff0000">hello</font>'))
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_verse, '<font color="#cC0000">hello</font>'))
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_verse, '<font color="#f00">hello</font>'))
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_verse, '<font color="#c00">hello</font>'))
        self.assertEqual('<font color="#ff0000">hello</font>', bs(html_fix_verse, '<font color="#c00" some_tag="data">hello</font>'))

        # Red, verse
        self.assertEqual('<span aria-hidden="true" class="verse">1.42</span>', bs(html_fix_verse, '<font color="#f00"> 1.42 </font>'))

        # Pre-existing verse
        self.assertEqual('<span aria-hidden="true" class="verse">42</span>', bs(html_fix_verse, '<span class="verse_number" disabled="true">42</span>'))

    def test_html_fix_paragraph(self):
        from lib.postprocessor import html_fix_paragraph

        # Noop
        self.assertEqual('',                                  bs(html_fix_paragraph, ''))
        self.assertEqual('<p>hello</p><p>world</p>',          bs(html_fix_paragraph, '<p>hello</p><p>world</p>'))
        self.assertEqual('<p>hello</p><p>nice<br/>world</p>', bs(html_fix_paragraph, '<p>hello</p><p>nice<br/>world</p>'))

        # Simple paragraph wrap
        self.assertEqual('', bs(html_fix_paragraph, '<br>'))
        self.assertEqual('<p>hello</p>', bs(html_fix_paragraph, 'hello'))
        self.assertEqual('<p>hello</p>', bs(html_fix_paragraph, '<br>hello'))
        self.assertEqual('<p>world</p>', bs(html_fix_paragraph, '<br/>world'))

        # Trim empty p
        self.assertEqual('<p>Hello</p>', bs(html_fix_paragraph, '<p></p><p>Hello</p>'))

        # Paragraph reconstruction and cleanup
        self.assertEqual('<p>hello<br/>world</p>',              bs(html_fix_paragraph, 'hello<br/>world'))
        self.assertEqual('<p>hello</p><p>nice</p><p>world</p>', bs(html_fix_paragraph, 'hello<br/><br><br/>nice<br/><br/><br/>world'))
        self.assertEqual('<p>hello<br/>nice</p><p>world</p>',   bs(html_fix_paragraph, 'hello<br/>nice<br/><br/><br/>world'))
        self.assertEqual('<p>hello world</p>',                  bs(html_fix_paragraph, 'hello world<br/><br/>'))

        # Paragraph cleaner
        self.assertEqual('<p>world</p>', bs(html_fix_paragraph, '<p style="text-decoration: underline;" class="hello">world</p>'))

        # Regression test for lecture / 23/06/2017
        self.assertEqual(u'<p>J\'ai vu l\'eau vive!</p>', bs(html_fix_paragraph, u'<br /><br /><p>J\'ai vu l\'eau vive!</p>'))

        # Regression test for vepre/intercession 12/01/2019
        # Some "br" elems were not wrapped in "p", thus causing the line fixer to crash
        self.assertEqual(u'<p>begin</p><p><br/>end</p>', bs(html_fix_paragraph, u'<p>begin</p>\n<br/>end'))

        # Validate complex paragraph reconstruction where paragraphs are in the middle of text
        self.assertEqual(u'<p>begin</p><p><br/>end</p>', bs(html_fix_paragraph, u'<p>begin</p>\n<br/>end'))
        self.assertEqual(u'<p>begin</p><p><br/><i>end</i></p>', bs(html_fix_paragraph, u'<p>begin</p>\n<br/><i>end</i>'))
        self.assertEqual(u'<p>begin</p><p><br/><i>middle</i></p><p>end</p>', bs(html_fix_paragraph, u'<p>begin</p>\n<br/><i>middle</i><p>end</p>'))
        self.assertEqual(u'<p><i>begin</i></p><p>end</p>', bs(html_fix_paragraph, u'\n<br/><i>begin</i><p>end</p>'))

    def test_html_fix_lines(self):
        from lib.postprocessor import html_fix_lines

        # Noop
        self.assertEqual('', bs(html_fix_lines, ''))
        self.assertEqual('<p><span class="line line-wrap" id="test-key-0" tabindex="0">hello</span><span class="line line-wrap" id="test-key-1" tabindex="0">world</span></p>',        bs(html_fix_lines, '<p><span class="line line-wrap">hello</span><span class="line line-wrap">world</span></p>'))
        self.assertEqual('<p><span class="line line-wrap" id="test-key-0" tabindex="0">hello</span></p><p><span class="line line-wrap" id="test-key-1" tabindex="0">world</span></p>', bs(html_fix_lines, '<p><span class="line line-wrap">hello</span></p><p><span class="line line-wrap">world</span></p>'))

        # Simple line wrap
        self.assertEqual('<p><span class="line" id="test-key-0" tabindex="0">hello world</span></p>', bs(html_fix_lines, '<p>hello world</p>'))

        # Nested line wrap
        self.assertEqual('<p><span class="line line-wrap" id="test-key-0" tabindex="0"><strong>hello</strong></span><span class="line line-wrap" id="test-key-1" tabindex="0"><strong>world</strong></span></p>', bs(html_fix_lines, '<p><strong>hello<br/>world</strong></p>'))

        # Trim empty line
        self.assertEqual('<p><span class="line" id="test-key-0" tabindex="0">Hello</span></p>', bs(html_fix_lines, '<p><br/>Hello</p>'))

        # Line reconstruction
        self.assertEqual('<p><span class="line line-wrap" id="test-key-0" tabindex="0">hello</span><span class="line line-wrap" id="test-key-1" tabindex="0">world</span></p><p><span class="line line-wrap" id="test-key-2" tabindex="0">hello</span><span class="line line-wrap" id="test-key-3" tabindex="0">world</span></p>', bs(html_fix_lines, '<p>hello<br/>world</p><p>hello<br/>world</p>'))
        self.assertEqual('<p><span class="line" id="test-key-0" tabindex="0">aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</span></p>', bs(html_fix_lines, '<p>aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</p>'))
        self.assertEqual('<p><span class="line" id="test-key-0" tabindex="0">aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</span></p>', bs(html_fix_lines, '<p>aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</p>'))
        self.assertEqual('<p><span class="line" id="test-key-0" tabindex="0">hello world</span></p>', bs(html_fix_lines, '<p><br/>hello world</p>'))

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
        self.assertEqual(u'\xa0; ', fix_common_typography(u'    ;  '))
        self.assertEqual(u'\xa0;', fix_common_typography(u'&nbsp;;'))
        self.assertEqual(u'\xa0;', fix_common_typography(u'&nbsp; ;'))
        self.assertEqual(u'Hello world\xa0! ', fix_common_typography(u'Hello world!'))
        self.assertEqual(u' «\xa0Hello World\xa0» ', fix_common_typography(u'«Hello World»'))
        self.assertEqual(u' «\xa0Hello World\xa0» ', fix_common_typography(u'&laquo;Hello World&raquo;'))

    def test_fix_case(self):
        from lib.postprocessor import fix_case

        self.assertEqual(u'Homélie d\'Origène sur le Lévitique', fix_case(u'HOMELIE D\'ORIGÈNE SUR LE LÉVITIQUE'))
        self.assertEqual(u'Sermon de saint L\xe9on le grand pour l\'anniversaire de son ordination', fix_case(u'SERMON DE S. LÉON LE GRAND POUR L\'ANNIVERSAIRE DE SON ORDINATION'))
        self.assertEqual(u'Homélie du II° siècle', fix_case(u'HOMELIE DU II° SIECLE'))
        self.assertEqual(u'Jean-Paul II', fix_case(u'JEAN-PAUL II'))
        self.assertEqual(u'Lettre encyclique du pape Pie XI pour le III° centenaire de la mort de saint Josaphat', fix_case(u'LETTRE ENCYCLIQUE DU PAPE PIE XI POUR LE III° CENTENAIRE DE LA MORT DE SAINT JOSAPHAT'))

    def test_fix_abbrev(self):
        from lib.postprocessor import fix_abbrev

        self.assertEqual(u'première', fix_abbrev(u'1ère'))
        self.assertEqual(u'premier', fix_abbrev(u'1er'))
        self.assertEqual(u'deuxième', fix_abbrev(u'2ème'))
        self.assertEqual(u'quatrième', fix_abbrev(u'4ème'))
        self.assertEqual(u'neuvième', fix_abbrev(u'9ème'))
        self.assertEqual(u'seizième', fix_abbrev(u'16ème'))
        self.assertEqual(u'dix-huitième', fix_abbrev(u'18ème'))
        self.assertEqual(u'vingt-et-unième', fix_abbrev(u'21ème'))

    def test_clean_ref(self):
        from lib.postprocessor import clean_ref

        self.assertEqual(u'', clean_ref(u''))
        self.assertEqual(u'Luc 1,32', clean_ref(u'Luc 1,32'))
        self.assertEqual(u'1jn 4, 11-21', clean_ref(u'1jn 4, 11-21'))
        self.assertEqual(u'1M 1, 41-64', clean_ref(u'1M 1, 41-64'))

        self.assertEqual(u'1A', clean_ref(u'1A'))
        self.assertEqual(u'1 12-13', clean_ref(u'1 12-13'))

        self.assertEqual(u'Ps 1A', clean_ref(u'1A', lecture_type='psaume'))
        self.assertEqual(u'Ps 1 12-13', clean_ref(u'1 12-13', lecture_type='psaume'))

