import unittest
from bs4 import BeautifulSoup

# verse number
# paragraphs
# intercession
# lines
# tipography
# inflexion (*+) --> <sup>

def t2bs(data): return BeautifulSoup(data, 'html5lib')
def bs2t(data): return str(data.body)[6:-7]
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
        self.assertEqual('<p>J\'ai vu l\'eau vive!</p>', bs(html_fix_paragraph, '<br /><br /><p>J\'ai vu l\'eau vive!</p>'))

        # Regression test for vepre/intercession 12/01/2019
        # Some "br" elems were not wrapped in "p", thus causing the line fixer to crash
        self.assertEqual('<p>begin</p><p><br/>end</p>', bs(html_fix_paragraph, '<p>begin</p>\n<br/>end'))

        # Validate complex paragraph reconstruction where paragraphs are in the middle of text
        self.assertEqual('<p>begin</p><p><br/>end</p>', bs(html_fix_paragraph, '<p>begin</p>\n<br/>end'))
        self.assertEqual('<p>begin</p><p><br/><i>end</i></p>', bs(html_fix_paragraph, '<p>begin</p>\n<br/><i>end</i>'))
        self.assertEqual('<p>begin</p><p><br/><i>middle</i></p><p>end</p>', bs(html_fix_paragraph, '<p>begin</p>\n<br/><i>middle</i><p>end</p>'))
        self.assertEqual('<p><i>begin</i></p><p>end</p>', bs(html_fix_paragraph, '\n<br/><i>begin</i><p>end</p>'))

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
        self.assertEqual('',      fix_common_typography(''))
        self.assertEqual('Père',  fix_common_typography('Pere'))
        self.assertEqual('père',  fix_common_typography('pere'))
        self.assertEqual('degré', fix_common_typography('degre'))
        self.assertEqual('cœur',  fix_common_typography('coeur'))
        self.assertEqual('cœur',  fix_common_typography('coeur'))

        # Typography
        self.assertEqual('\xa0', fix_common_typography('&nbsp;'))
        self.assertEqual('\xa0; ', fix_common_typography('    ;  '))
        self.assertEqual('\xa0; ', fix_common_typography('&nbsp;;'))
        self.assertEqual('\xa0; ', fix_common_typography('&nbsp; ;'))
        self.assertEqual('Hello world\xa0! ', fix_common_typography('Hello world!'))
        self.assertEqual(' «\xa0Hello World\xa0» ', fix_common_typography('«Hello World»'))
        self.assertEqual(' «\xa0Hello World\xa0» ', fix_common_typography('&laquo;Hello World&raquo;'))

    def test_fix_case(self):
        from lib.postprocessor import fix_case

        self.assertEqual('Homélie de saint Bède le vénérable', fix_case('HOMÉLIE DE S. BÈDE LE VÉNÉRABLE'))
        self.assertEqual('Homélie d\'Origène sur le Lévitique', fix_case('HOMELIE D\'ORIGÈNE SUR LE LÉVITIQUE'))
        self.assertEqual('Sermon de saint L\xe9on le grand pour l\'anniversaire de son ordination', fix_case('SERMON DE S. LÉON LE GRAND POUR L\'ANNIVERSAIRE DE SON ORDINATION'))
        self.assertEqual('Homélie du II° siècle', fix_case('HOMELIE DU II° SIECLE'))
        self.assertEqual('Jean-Paul II', fix_case('JEAN-PAUL II'))
        self.assertEqual('Lettre encyclique du pape Pie XI pour le III° centenaire de la mort de saint Josaphat', fix_case('LETTRE ENCYCLIQUE DU PAPE PIE XI POUR LE III° CENTENAIRE DE LA MORT DE SAINT JOSAPHAT'))

    def test_fix_number_abbrev(self):
        from lib.postprocessor import fix_number_abbrev

        self.assertEqual('première', fix_number_abbrev('1ère'))
        self.assertEqual('premier', fix_number_abbrev('1er'))
        self.assertEqual('deuxième', fix_number_abbrev('2ème'))
        self.assertEqual('quatrième', fix_number_abbrev('4ème'))
        self.assertEqual('neuvième', fix_number_abbrev('9ème'))
        self.assertEqual('seizième', fix_number_abbrev('16ème'))
        self.assertEqual('dix-huitième', fix_number_abbrev('18ème'))
        self.assertEqual('vingt-et-unième', fix_number_abbrev('21ème'))

    def test_clean_ref(self):
        from lib.postprocessor import clean_ref

        self.assertEqual('', clean_ref(''))
        self.assertEqual('Luc 1,32', clean_ref('Luc 1,32'))
        self.assertEqual('1jn 4, 11-21', clean_ref('1jn 4, 11-21'))
        self.assertEqual('1M 1, 41-64', clean_ref('1M 1, 41-64'))

        self.assertEqual('1A', clean_ref('1A'))
        self.assertEqual('1 12-13', clean_ref('1 12-13'))

        self.assertEqual('Ps 1A', clean_ref('1A', lecture_type='psaume'))
        self.assertEqual('Ps 1 12-13', clean_ref('1 12-13', lecture_type='psaume'))

class TestOfficePostprocessor(unittest.TestCase):
    def test_antienne_propagation(self):
        from lib.postprocessor import postprocess_antienne_67

        lectures = [
            [{
                'type': 'hymne',
                'antienne': 'hymn antienne'
            }],
            [{
                'type': 'psaume',
                'antienne': 'hymn for all psalms'
            }],
            [{
                'type': 'psaume',
                'antienne': '' # Empty antienne, still nominal
            }],
            [{
                'type': 'psaume',
                # Missing antienne field: still nominal
            }],
            [{
                'type': 'psaume',
                'antienne': 'some new antienne' # must be preserved
            }],
            [{
                # Missing type, must not crash
                # Missing antienne field: still nominal
            }],
            [{
                'type': 'psaume',
                'antienne': '2 psalms antienne'
            }],
            [{
                'type': 'psaume',
            }],
        ]

        postprocess_antienne_67(67, 'prod', {'variants': [{'lectures': lectures}]})

        # Validate antienne field
        assert lectures[0][0]['antienne'] == 'hymn antienne'
        assert lectures[1][0]['antienne'] == 'hymn for all psalms'
        assert lectures[2][0]['antienne'] == 'hymn for all psalms'
        assert lectures[3][0]['antienne'] == 'hymn for all psalms'
        assert lectures[4][0]['antienne'] == 'some new antienne'
        assert 'antienne' not in lectures[5][0]
        assert lectures[6][0]['antienne'] == '2 psalms antienne'
        assert lectures[7][0]['antienne'] == '2 psalms antienne'

        # Validate has_antienne field
        assert lectures[0][0]['has_antienne'] == 'both' # Hymn
        assert lectures[1][0]['has_antienne'] == 'initial'
        assert lectures[2][0]['has_antienne'] == 'none'
        assert lectures[3][0]['has_antienne'] == 'final'
        assert lectures[4][0]['has_antienne'] == 'both'
        assert lectures[5][0]['has_antienne'] == 'none'
        assert lectures[6][0]['has_antienne'] == 'initial'
        assert lectures[7][0]['has_antienne'] == 'final'

    def test_doxology_rules_exceptions(self):
        from lib.postprocessor import postprocess_doxology_67

        lectures = [
            [{
                'type': 'psaume',
                'reference': "   DN    3   , 42-12", # No doxology, however mis-spelt this is
            }],
        ]

        postprocess_doxology_67(67, 'prod', {'variants': [{'lectures': lectures}]})

        # Validate has_doxology field
        assert lectures[0][0]['has_doxology'] is False # Dn 3

    def test_doxology_rules_not_psalms(self):
        from lib.postprocessor import postprocess_doxology_67

        lectures = [
            [{
                # Not a psalm, not even a type
            }],
            [{
                'type': 'hymne', # Not a psalm
            }],
        ]

        postprocess_doxology_67(67, 'prod', {'variants': [{'lectures': lectures}]})

        # Validate has_doxology field
        assert lectures[0][0]['has_doxology'] is False # Missing type
        assert lectures[1][0]['has_doxology'] is False # Not a psalm

    def test_doxology_rules_nominal(self):
        from lib.postprocessor import postprocess_doxology_67

        # Nominal: 3 distinct consecutive psalms
        lectures = [
            [{
                'type': 'psaume',
                'reference': "Ps 42",
            }],
            [{
                'type': 'psaume',
                'reference': "Ps 43",
            }],
            [{
                'type': 'psaume',
                'reference': "Ps 44",
            }],
        ]

        postprocess_doxology_67(67, 'prod', {'variants': [{'lectures': lectures}]})

        # Validate has_doxology field
        assert lectures[0][0]['has_doxology'] is True
        assert lectures[1][0]['has_doxology'] is True
        assert lectures[2][0]['has_doxology'] is True

    def test_doxology_rules_split_3_shared_antienne(self):
        from lib.postprocessor import postprocess_doxology_67

        # Psalm 101 is split into 3 parts in the lecture's office, with a shared antienne
        lectures = [
            [{
                'type': 'psaume',
                'reference': "Ps 101-I",
                'has_antienne': 'initial',
            }],
            [{
                'type': 'psaume',
                'reference': "Ps 101-II",
                'has_antienne': 'intermediate',
            }],
            [{
                'type': 'psaume',
                'reference': "Ps 101-II",
                'has_antienne': 'final',
            }],
        ]

        postprocess_doxology_67(67, 'prod', {'variants': [{'lectures': lectures}]})

        # Validate has_doxology field
        assert lectures[0][0]['has_doxology'] is False
        assert lectures[1][0]['has_doxology'] is False
        assert lectures[2][0]['has_doxology'] is True

    def test_doxology_rules_split_3_dedicated_antienne(self):
        from lib.postprocessor import postprocess_doxology_67

        # Psalm 101 is split into 3 parts in the lecture's office, with a dedicated antienne
        lectures = [
            [{
                'type': 'psaume',
                'reference': "Ps 101-I",
                'has_antienne': 'both',
            }],
            [{
                'type': 'psaume',
                'reference': "Ps 101-II",
                'has_antienne': 'both',
            }],
            [{
                'type': 'psaume',
                'reference': "Ps 101-II",
                'has_antienne': 'both',
            }],
        ]

        postprocess_doxology_67(67, 'prod', {'variants': [{'lectures': lectures}]})

        # Validate has_doxology field
        assert lectures[0][0]['has_doxology'] is True
        assert lectures[1][0]['has_doxology'] is True
        assert lectures[2][0]['has_doxology'] is True

    def test_doxology_rules_split_1_psalm_then_2_shared_antienne(self):
        from lib.postprocessor import postprocess_doxology_67

        # In the sexte office, we get 118-18, 87-I and 87-2. Depending on period of the year, they may or may not share antienne
        lectures = [
            [{
                'type': 'psaume',
                'reference': "Ps 118-18",
                'has_antienne': 'initial',
            }],
            [{
                'type': 'psaume',
                'reference': "Ps 87-I",
                'has_antienne': 'intermediate',
            }],
            [{
                'type': 'psaume',
                'reference': "Ps 87-II",
                'has_antienne': 'final',
            }],
        ]

        postprocess_doxology_67(67, 'prod', {'variants': [{'lectures': lectures}]})

        # Validate has_doxology field
        assert lectures[0][0]['has_doxology'] is True
        assert lectures[1][0]['has_doxology'] is False
        assert lectures[2][0]['has_doxology'] is True
