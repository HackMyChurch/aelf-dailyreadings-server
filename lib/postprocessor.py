import re
import html
import datetime
import hunspell
import unidecode
from bs4 import BeautifulSoup, NavigableString, Tag, Comment

from .constants import ID_TO_TITLE
from .constants import DETERMINANTS
from .constants import HTML_BLOCK_ELEMENTS
from .office import get_lecture_variants_by_type
from .group import group_related_items, group_lecture_variants

#
# Utils
#

def _parse_date(date_string) -> datetime.date:
    year, month, day = date_string.split('-')
    return datetime.date(int(year), int(month), int(day))

def is_int(data):
    try:
        int(data)
    except:
        return False
    return True

def _is_letter(data):
    if not data:
        return False

    for c in data.lower():
        if ord(c) < ord('a') or ord(c) > ord('z'):
            return False
    return True

PSALM_MATCH=re.compile(r'^[0-9]+(-[IV0-9]+)?$')
def _is_psalm_ref(data):
    if not data:
        return False

    return re.match(PSALM_MATCH, data.replace(' ', ''))

VERSE_REF_MATCH=re.compile(r'^[0-9]+[A-Z]?(\.[0-9]+)?$')
def _is_verse_ref(data):
    if not data:
        return False

    return re.match(VERSE_REF_MATCH, data.replace(' ', ''))

ROMAN_NUMBER_MATCH=re.compile(r'^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$')
def _is_roman_number(data):
    if not data:
        return False

    return re.match(ROMAN_NUMBER_MATCH, data.upper())

def lecture_is_psalm(lecture) -> bool:
    if lecture.get('type') != 'psaume':
        return False

    lecture_ref = lecture.get("reference", "")
    if not lecture_ref.lower().startswith('ps'):
        return False

    return True


# FIXME: this is very hackish. We'll need to replace this with a real parser
def clean_ref(ref, lecture_type=None):
    ref = ref.strip()

    # Remove any leading 'cf.'
    if ref.lower().startswith('cf.'):
        ref = ref[3:].lstrip()

    # Add 'Ps' if missing
    if lecture_type == "psaume" and not ref.lower().startswith('ps') and not _is_letter(ref[0]):
        ref = 'Ps %s' % ref

    return ref

PARENTHESIS_MATCHER=re.compile(r'(\(.*\)|\[.*\])')
def strip_parenthesis(line: str) -> str:
    line = re.sub(PARENTHESIS_MATCHER, '', line)
    line.replace('  ', ' ')
    return line

def _filter_fete(fete):
    '''fete can be processed from 2 places. Share common filtering code'''
    fete = fete.strip()
    fete = fix_abbrev(fete)
    fete = fix_number_abbrev(fete)

    verbe = "fêtons" if 'saint' in fete.lower() else "célèbrons"
    text = ''

    # Single word (paque, ascension, noel, ...)
    if fete and ' ' not in fete and fete.lower() not in ['ascension', 'pentecôte']:
        text += " Nous %s %s" % (verbe, fete)
    # Standard fete
    elif fete and 'férie' not in fete.lower():
        pronoun = get_pronoun_for_sentence(fete)
        text += ' Nous %s %s%s' % (verbe, pronoun, fete)
    else:
        text += fete

    return text

def _id_to_title(data):
    '''
    Forge a decent title from and ID as a fallback when the API does not provide a title
    '''
    if data in ID_TO_TITLE:
        return ID_TO_TITLE[data]

    chunks = data.split('_')
    try:
        int(chunks[-1])
    except:
        pass
    else:
        chunks.pop()
    return (' '.join(chunks)).capitalize()

def _wrap_node_children(soup, parent, name, *args, **kwargs):
    '''
    Wrap all children of a bs4 node into an intermediate node.
    '''
    intermediate = soup.new_tag(name, *args, **kwargs)

    # Do /not/ remove the list. It prevents the node deduplication done by bs4
    # which in turn breaks the pargraph detection
    for content in list(parent.contents):
        intermediate.append(content)
    parent.clear()
    parent.append(intermediate)

def _split_node_parent(soup, name, first, last=None, keep_delimiters=False, **kwargs):
    '''
    Split first's parent tag from first to last tags. If any of the resulting tag
    is empty, drop it.
    '''
    last = last or first
    if first.parent != last.parent:
        raise ValueError("First and Last MUST have the same parent")

    # Create and insert new element
    current_parent = first.parent
    new_parent = soup.new_tag(current_parent.name)
    new_parent.attrs = current_parent.attrs
    current_parent.insert_before(new_parent)

    # We'll delete content only between these 2 tags
    first['__first_node'] = True
    last ['__last_node']  = True

    # Move text elements to new container
    for content in list(current_parent.contents):
        if isinstance(content, Tag) and content.get('__first_node'):
            break
        new_parent.append(content.extract())

    # Remove the elements between first and last
    for content in list(current_parent.contents):
        content.extract()

        if keep_delimiters:
            new_parent.append(content.extract())

        if isinstance(content, Tag) and content.get('__first_node'):
            del first['__first_node']

        if isinstance(content, Tag) and content.get('__last_node'):
            del first['__last_node']
            break

    # Recurse
    if current_parent.name != name:
        _split_node_parent(soup, name, new_parent, keep_delimiters=True, **kwargs)
    for key, value in list(kwargs.items()):
        if key not in current_parent.attrs or current_parent.attrs[key] != value:
            _split_node_parent(soup, name, new_parent, keep_delimiters=True, **kwargs)

    # Make sure neither container is empty
    for parent in [new_parent, current_parent]:
        if not parent.contents:
            parent.extract()

#
# API
#

NUMBER_TO_WORDS = {
    '1':  'un',
    '2':  'deux',
    '3':  'trois',
    '4':  'quatre',
    '5':  'cinq',
    '6':  'six',
    '7':  'sept',
    '8':  'huit',
    '9':  'neuf',
    '10': 'dix',
    '11': 'onze',
    '12': 'douze',
    '13': 'treize',
    '14': 'quatorze',
    '15': 'quinze',
    '16': 'seize',
    '20': 'vingt',
}

def _fix_number_abbrev(match):
    number = match.group(1)
    abbrev = match.group(2)
    word = ''

    if number == '1':
        word = 'prem'
    elif number in NUMBER_TO_WORDS:
        word = NUMBER_TO_WORDS[number]
    elif len(number) == 2 and number[0]+"0" in NUMBER_TO_WORDS and number[1] in NUMBER_TO_WORDS:
        words = [NUMBER_TO_WORDS[number[0]+"0"], NUMBER_TO_WORDS[number[1]]]
        if number[1] == '1':
            words.insert(1, 'et')
        word = '-'.join(words)
    else:
        return match.group(1) + match.group(2)

    if word[-1] == 'e':
        word = word[:-1]
    elif word[-1] == 'f':
        word = word[:-1]+'v'
    elif word[-1] == 'q':
        word = word+'u'

    return word + 'i' + abbrev


def fix_abbrev(sentence):
    # Fix word splitting when multiple Saints
    sentence = re.sub(r'(\w)(S\.|St|Ste) ', r'\1, \2 ', sentence)

    # Fix abbrev itself
    sentence = sentence.replace("S. ",  "saint ")\
                       .replace("S.",   "saint ")\
                       .replace("St ",  "saint ")\
                       .replace("Ste ", "sainte ")

    return sentence

def fix_number_abbrev(sentence: str) -> str:
    return re.sub(r'([0-9]+)([èe](re?|me))', _fix_number_abbrev, sentence)

HTML_TAG_MATCH=re.compile('(<!--.*?-->|<[^>]*>)')
def strip_html(sentence):
    '''
    Remove all HTML tags from sentence
    '''
    return HTML_TAG_MATCH.sub(' ', sentence)

FR_DICT=hunspell.HunSpell('fr-classique.dic', 'fr-classique.aff')
def _fix_word_case(match):
    word = match.group()
    sentence = match.string

    # Get char following the match, this is used for roman number disambiguation
    next_char = ''
    if match.end() < len(sentence):
        next_char = sentence[match.end()]

    # Skip roman number
    if _is_roman_number(word) and next_char != "'":
        return word.upper()

    # If there is no diacritics, these might be missing
    if unidecode.unidecode(word) == word:
        if not FR_DICT.spell(word):
            for suggestion in FR_DICT.suggest(word):
                # Accept suggestion if only diacritics changed
                if unidecode.unidecode(word) == unidecode.unidecode(suggestion):
                    word = suggestion
                    break

    # If there is a single letter, lower case
    if len(word) <= 1:
        return word.lower()

    # If there are no known stems, assume proper name and capitalize
    stems = FR_DICT.stem(word)
    if not stems:
        return word.capitalize()

    # If all the possible stem word start with a lowercase, lower
    if all((stem.decode('utf8')[0].islower() for stem in stems)):
        return word.lower()
    else:
        return word.capitalize()

WORD_MATCH=re.compile(r'\w+', re.UNICODE)
def fix_case(sentence):
    '''
    Take a potentially all caps sentence as input and make it readable
    '''
    sentence = fix_abbrev(sentence)
    sentence = fix_number_abbrev(sentence)

    # Make sure to start with a upper letter
    sentence = sentence[0].upper() + sentence[1:]

    # Heuristic: Only apply the following if the sentence has more than 5 char AND more than half capital letters
    if len(sentence) < 5:
        return sentence

    upper_case_letters_count = 0
    all_letters_count = 0
    for c in sentence:
        if not c.isalnum():
            continue
        all_letters_count += 1

        if c.isupper():
            upper_case_letters_count += 1

    if (upper_case_letters_count < all_letters_count / 3):
        return sentence

    # Fix individual words case
    sentence = re.sub(WORD_MATCH, _fix_word_case, sentence)

    # Make sure punctuation is followed by an upper case letter
    sentence = re.sub(r'([.:!?«»()]\s*)([a-z])', lambda match: match.group(1) + match.group(2).upper(), sentence)

    # Make sure to start with a upper letter
    sentence = sentence[0].upper() + sentence[1:]

    return sentence

def fix_common_typography(text):
    '''
    Generic search and replace fixes
    '''
    # Decode entities so that we do not accidentally break them
    text = html.unescape(text)

    # Simple replaces
    text = text.replace('fete', 'fête')\
               .replace('degre', 'degré')\
               .replace('oe', 'œ')\
               .replace('n\\est', 'n\'est')\

    # Preg replaces
    text = re.sub(r'([Pp])ere', '\\1ère', text)
    text = re.sub(r'[Ee]glise', 'Église', text)

    # Typography
    text = re.sub(r'\s*-\s*',      '-',    text)
    text = re.sub(r':\s+(\s+)'  ,  '',     text)
    text = re.sub(r'\s*\(',        ' (',   text)
    text = re.sub(r'\s*\u00a0\s*', '\u00a0', text) # Mixed type of blanks

    text = re.sub(r'\s*»',          '\u00a0» ',  text) # Typographic quote
    text = re.sub(r'«\s*',          ' «\u00a0',  text)
    text = re.sub(r'\s*([:?!])\s*', '\u00a0\\1 ', text)
    text = re.sub(r'\s+;\s*',       '\u00a0; ',  text) # Semicolon, prefixed by a blank

    return text

def fix_rv(text):
    '''
    Quick and dirty port of the "rv" formatting. Detects R/ and V/ in the offices
    and turn it bold. As this is upper case, we can assume that it will not
    collide with tags name, hence bypass the overhead of bs4
    '''
    text = text.replace('R/', '<strong>R/</strong>')
    text = text.replace('V/', '<strong>V/</strong>')
    return text

def get_pronoun_for_sentence(sentence):
    words = [w.lower() for w in sentence.split(" ")]

    # Argh, hard coded exception
    if words[0] in ['saint', 'sainte'] and "trinité" not in sentence.lower():
        return ''

    # Already a determinant or equivalent
    if words[0] in DETERMINANTS:
        return ''

    # If it starts by a vowel, that's easy, don't care about M/F
    if words[0][0] in ['a', 'e', 'ê', 'é', 'è', 'i', 'o', 'u', 'y']:
        return "l'"

    # Attempt to guess M/F by checking if 1st words ends with 'e'. Default on F
    masc = ['sacré-c\\u0153r', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    if (words[0] in masc) or (len(words) > 1 and words[1] in masc):
        return "le "

    return "la "

def postprocess_informations_legacy(informations):
    '''
    Generate 'text' key in an information dict from json API
    '''
    text = ""
    fete_skip = False
    jour_lit_skip = False

    # Cleanup fete
    informations['fete'] = fix_abbrev(informations.get('fete', ''))
    informations['fete'] = fix_number_abbrev(informations.get('fete', ''))

    # Never print fete if this is the semaine
    day_name = informations.get('jour') or ''
    liturgical_day_name = informations.get('jour_liturgique_nom') or ''
    liturgical_week_name = informations.get('semaine') or ''
    if liturgical_day_name.split(' ')[0] == liturgical_week_name.split(' ')[0]:
        jour_lit_skip = True
    if liturgical_day_name == informations.get('fete', '') and 'férie' not in informations.get('fete', '').lower():
        jour_lit_skip = True
    if informations['fete'] == informations.get('degre', ''):
        fete_skip = True

    if not jour_lit_skip and 'jour_liturgique_nom' in informations and 'férie' not in liturgical_day_name.lower():
        text += _filter_fete(liturgical_day_name)
    elif day_name:
        text += day_name.strip()
        if not jour_lit_skip and liturgical_day_name:
            text += ' %s' % _filter_fete(liturgical_day_name)

    if liturgical_week_name:
        if text:
            text += ', '
        text += liturgical_week_name

        numero = re.match('^[0-9]*', liturgical_week_name).group()
        numero = ((int(numero)-1) % 4) + 1 if numero else ""
        semaines = {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}
        if numero in semaines:
            text += " (semaine %s du psautier)" % semaines[numero]

    if 'annee' in informations:
        if text:
            text += " de l'année %s" % informations['annee']
        else:
            text += "Année %s" % informations['annee']

    if text:
        text += "."

    if not fete_skip and 'fete' in informations and (not day_name or day_name not in informations['fete']):
        fete = _filter_fete(informations['fete'])
        if fete and not 'férie' in fete.lower():
            text += "%s." % fete

    if 'couleur' in informations:
        text += " La couleur liturgique est le %s." % informations['couleur']

    # Final cleanup: 1er, 1ère, 2ème, 2nd, ... --> exponent
    text = re.sub(r'([0-9])(er|nd|ère|ème) ', r'\1<sup>\2</sup> ', text)
    text = text[:1].upper() + text[1:]

    # Inject text
    informations['text'] = text.strip()
    return informations

def shorten_liturgical_day(date: datetime.date, liturgical_day_name: str, is_solemnity: bool) -> str:
    liturgical_day_name_lower = liturgical_day_name.lower()

    # Feast for which we display a short name
    if 'nativité' in liturgical_day_name_lower and 'marie' in liturgical_day_name_lower:
        return 'Nativité de\u00a0Marie'
    elif 'évangéliste' in liturgical_day_name_lower:
        if 'matthieu' in liturgical_day_name_lower:
            return 'Saint\u00a0Matthieu'
        elif 'marc' in liturgical_day_name_lower:
            return 'Saint\u00a0Marc'
        elif 'luc' in liturgical_day_name_lower:
            return 'Saint\u00a0Luc'
        elif 'jean' in liturgical_day_name_lower:
            return 'Saint\u00a0Jean'
    elif (date.day, date.month) == (2, 11):
        return 'Fidèles\u00a0défunts'
    elif (date.day, date.month) == (2, 2):
        return 'Présentation au\u00a0Temple'
    elif "cendre" in liturgical_day_name_lower and date.isoweekday() == 3:
        return 'Cendres'
    elif 'croix glorieuse' in liturgical_day_name_lower:
        return 'Croix\u00a0Glorieuse'
    elif 'transfiguration' in liturgical_day_name_lower:
        return 'Transfiguration'
    elif 'visitation' in liturgical_day_name_lower:
        return 'Visitation'

    # After that, only consider solemnities
    if not is_solemnity:
        return ''

    if 'dédicace' in liturgical_day_name_lower:
        return ''
    elif (date.day, date.month) == (1, 11):
        return 'Toussaint'
    elif 'christ' in liturgical_day_name_lower and 'roi' in liturgical_day_name_lower:
        return 'Christ-Roi'
    elif (date.day, date.month) == (8, 12):
        return 'Immaculée\u00a0Conception'
    elif (date.day, date.month) == (25, 12):
        return "Noël"
    elif 'épiphanie' in liturgical_day_name_lower:
        return 'Épiphanie'
    elif (date.day, date.month) == (1, 1):
        return 'Sainte\u00a0Marie, Mère\u00a0de\u00a0Dieu'
    elif (date.day, date.month) == (19, 3):
        return 'Saint\u00a0Joseph'
    elif 'rameaux' in liturgical_day_name_lower:
        return 'Rameaux'
    elif 'résurrection' in liturgical_day_name_lower:
        return 'Pâques'
    elif 'miséricorde' in liturgical_day_name_lower:
        return 'Miséricorde'
    elif 'octave' in liturgical_day_name_lower:
        return ''
    elif 'annonciation' in liturgical_day_name_lower:
        return 'Annonciation'
    elif 'ascension' in liturgical_day_name_lower:
        return 'Ascension'
    elif 'trinité' in liturgical_day_name_lower:
        return 'Sainte\u00a0Trinité'
    elif 'sacrement' in liturgical_day_name_lower:
        return 'Saint\u00a0Sacrement'
    elif 'cœur' in liturgical_day_name_lower:
        return 'Sacré-Cœur'
    elif 'nativité' in liturgical_day_name_lower and 'baptiste' in liturgical_day_name_lower:
        return 'Saint\u00a0Jean\u00a0Baptiste'
    elif 'pierre' in liturgical_day_name_lower and 'paul' in liturgical_day_name_lower:
        return 'Saint\u00a0Pierre et Saint\u00a0Paul'
    elif 'assomption' in liturgical_day_name_lower:
        return 'Assomption'

    return liturgical_day_name

def compute_liturgical_year(date: datetime.date, liturgical_year_name: str, is_solemnity: bool) -> str:
    # First option, attempt to cleanup the input from AELF
    if liturgical_year_name:
        liturgical_year_name = liturgical_year_name.lower()
    if liturgical_year_name:
        return liturgical_year_name

    # Fallback: compute the cutoff date for this year
    christmas_date = datetime.date(date.year, 12, 25)
    last_advent_sunday_date = christmas_date - datetime.timedelta(days=christmas_date.isoweekday())
    first_sunday_of_next_liturgical_year = last_advent_sunday_date - datetime.timedelta(days=21)

    year = date.year
    if date >= first_sunday_of_next_liturgical_year:
        year += 1

    # Sunday or solemnity
    if is_solemnity or date.isoweekday == 7:
        return ['c', 'a', 'b'][year % 3]
    else:
        return ['paire', 'impaire'][year % 2]


FRENCH_DAYS=['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
def postprocess_informations_modern(informations):
    # Parse date
    date = _parse_date(informations['date'])

    # Extract the degree
    degree = informations.get('degre') or ''
    fete = informations.get('fete') or ''
    is_solemnity = 'solennité' in (degree or fete).lower()

    # Extract the liturgical day
    liturgical_day_name = informations.get('jour_liturgique_nom') or ''
    liturgical_day_name_short = shorten_liturgical_day(date, liturgical_day_name, is_solemnity)
    if liturgical_day_name_short:
        informations['liturgical_day'] = liturgical_day_name_short
    else:
        informations['liturgical_day'] = FRENCH_DAYS[date.weekday()]

    # Extract the liturgical year
    informations['liturgical_year'] = compute_liturgical_year(date, informations.get('annee') or '', is_solemnity)

    # Extract the liturgical time
    liturgical_period = informations.get('temps_liturgique', '')
    if not liturgical_period:
        if 'avent' in degree.lower():
            liturgical_period = 'avent'
        if 'noël' in degree.lower():
            liturgical_period = 'noel'
    informations['liturgical_period'] = liturgical_period

    # Extract the liturgical week, if possible
    informations['liturgical_week'] = None
    informations['psalter_week'] = None
    week_number = -1
    if week_description := informations.get('semaine'):
        week_number_match = re.search(r'^\d+', week_description)
        if week_number_match is not None:
            week_number = int(week_number_match.group())
    elif 'cendres' in liturgical_day_name.lower():
        week_number = 0

    if week_number >= 0:
        informations['liturgical_week'] = week_number
        informations['psalter_week'] = informations['liturgical_week'] % 4 or 4

    # Extract liturgical options
    informations['liturgy_options'] = []

    # Start by counting the number of options provided by AELF.
    if informations.get('couleur3'): options_count = 3
    elif informations.get('couleur2') or 'facultative' in (informations.get('ligne3') or ''): options_count = 2
    else: options_count = 1

    # Compute default degree and suffix, if any
    degree_suffix = ''
    default_degree = ''

    if liturgical_period == 'avent':
        degree_suffix = ' de l’Avent'
    elif liturgical_period == 'noel':
        degree_suffix = ' de Noël'
    elif liturgical_period == 'careme':
        degree_suffix = ' du Carême'
    elif liturgical_period == 'triduum':
        default_degree = 'Triduum Pascal'
    elif liturgical_period == 'pascal':
        degree_suffix = ' du temps Pascal'
    
    if not default_degree:
        default_degree = 'Férie'+degree_suffix
    if 'férie' in degree.lower():
        degree = default_degree

    # Get and clean the "lines"
    line1 = fix_common_typography(strip_parenthesis(fix_abbrev(informations.get('ligne1') or ''))).strip()
    line2 = fix_common_typography(strip_parenthesis(fix_abbrev(informations.get('ligne2') or ''))).strip()
    line3 = fix_common_typography(strip_parenthesis(fix_abbrev(informations.get('ligne3') or ''))).strip()
    fete = fix_common_typography(strip_parenthesis(fix_abbrev(informations.get('fete') or '')))

    if line2 and not line1:
        line1 = line2
        line2 = ""
    if line3 and not line2:
        line2 = line3
        line3 = ""

    # Remove redundant day from "line1" if this is an ordinary day
    liturgical_week = informations.get('semaine') or ''
    if liturgical_week and liturgical_week in line1:
        line1 = liturgical_week

    # Get the first option
    if options_count == 1:
        liturgical_name = ''
        if not degree:
            if line3 and line3[0] not in '[(':
                degree = line3
                liturgical_name = line2
            elif line2:
                degree = line2
                liturgical_name = line1
            else:
                degree = default_degree

        if 'férie' in degree.lower():
            degree = "Férie"+degree_suffix

        if not liturgical_name:
            if line3 and line3 not in degree and line3 not in fete:
                liturgical_name = line3
            elif line2 and line2 not in degree and line2 not in fete:
                liturgical_name = line2
            else:
                liturgical_name = line1

        informations['liturgy_options'].append({
            'liturgical_color': informations['couleur'],
            'liturgical_degree': degree,
            'liturgical_name': liturgical_name,
        })
    elif options_count == 2:
        informations['liturgy_options'].append({
            'liturgical_color': informations['couleur'],
            'liturgical_degree': degree or default_degree,
            'liturgical_name': line1,
        })

        liturgical_name = line2
        liturgical_degree = line3

        if liturgical_degree in liturgical_name:
            liturgical_name = liturgical_name.rsplit('.')[0]

        informations['liturgy_options'].append({
            'liturgical_color': informations.get('couleur2') or informations['couleur'],
            'liturgical_degree': liturgical_degree,
            'liturgical_name': liturgical_name,
        })
    elif options_count == 3:
        informations['liturgy_options'].append({
            'liturgical_color': informations['couleur'],
            'liturgical_degree': default_degree,
            'liturgical_name': line1,
        })

        for line, color in [(line2, informations['couleur2']), (line3, informations['couleur3'])]:
            name, degree = re.split(r"[.;]", line.rstrip(".,; \t"), 1)
            informations['liturgy_options'].append({
                'liturgical_color': color,
                'liturgical_degree': degree.strip(),
                'liturgical_name': name.strip(),
            })

    # Fix liturgical color of gaudete & laetare
    if informations.get('temps_liturgique') == 'careme' and week_number == 4 and date.isoweekday() == 7:
        informations['liturgy_options'][0]['liturgical_color'] = 'rose'
    if informations.get('temps_liturgique') == 'avent' and week_number == 3 and date.isoweekday() == 7:
        informations['liturgy_options'][0]['liturgical_color'] = 'rose'

    # Remove legacy keys not used anywhere
    if 'couleur'  in informations: del informations['couleur']
    if 'couleur2' in informations: del informations['couleur2']
    if 'couleur3' in informations: del informations['couleur3']
    if 'ligne1'   in informations: del informations['ligne1']
    if 'ligne2'   in informations: del informations['ligne2']
    if 'ligne3'   in informations: del informations['ligne3']
    if 'fete'     in informations: del informations['fete']
    if 'degre'    in informations: del informations['degre']
    if 'jour'     in informations: del informations['jour']

    return informations

def postprocess_informations(informations):
    informations = postprocess_informations_legacy(informations)
    informations = postprocess_informations_modern(informations)
    return informations

# FIXME: this function is only used by the libs and does not follow te same convention as the others
def lectures_common_cleanup(data):
    '''
    Walk on the variants and lectures lists and apply common cleanup code. This is where
    most of the current application's cleanup logic will migrate. In the mean time, filter
    the json to reproduce the old RSS API bugs (YEAH!)
    '''
    data['informations'] = postprocess_informations(data['informations'])

    # PASS 1: post-process lectures items
    for office_variant in data['variants']:
        for lecture_variants in office_variant['lectures']:
            for lecture in lecture_variants:
                # Title cleanup / compat with current applications
                name = lecture['key']
                if lecture['title']:
                    if name in ["hymne", "pericope", "lecture", "lecture_patristique"]:
                        if not lecture['title'][0] in ['«', "'", '"']:
                            lecture['title'] = "« %s »" % lecture['title']
                        lecture['title'] = "%s : %s" % (_id_to_title(name), lecture['title'])
                else:
                    lecture['title'] = _id_to_title(name)

                # Extract the office type from the key
                key = lecture['key']
                lecture['type'] = key.split('_')[0]

                # Remove number abbreviations from titles
                lecture['title'] = fix_abbrev(lecture['title'])
                lecture['title'] = fix_number_abbrev(lecture['title'])

                if lecture['reference']:
                    raw_ref = lecture['reference']
                    lecture['reference'] = clean_ref(raw_ref, lecture['type'])

                    if 'cantique' in lecture['reference'].lower():
                        lecture['title'] = lecture['reference']
                        if '(' in lecture['reference']:
                            lecture['reference'] = lecture['reference'].split('(')[1].split(')')[0]
                    elif lecture['title'] in "Pericope":
                        lecture['title'] = "%s : %s" % (lecture['title'], lecture['reference'])
                    elif lecture['title'] == "Psaume" and _is_psalm_ref(raw_ref):
                        lecture['title'] = "%s : %s" % (lecture['title'], raw_ref)
                    else:
                        lecture['title'] = "%s (%s)" % (lecture['title'], lecture['reference'])

                if name.split('_', 1)[0] in ['verset']:
                    lecture['title'] = 'verset'

                # FIXME: this hack is plain Ugly and there only to make newer API regress enough to be compatible with deployed applications
                title_sig = lecture['title'].strip().lower()
                if title_sig.split(' ')[0] in ['antienne']:
                    lecture['title'] = 'antienne'
                elif title_sig.split(' ')[0] in ['repons', 'répons']:
                    lecture['title'] = 'repons'
                elif title_sig.startswith('parole de dieu'):
                    reference = lecture['title'].rsplit(':', 1)
                    if len(reference) > 1:
                        lecture['title'] = 'Pericope : (%s)' % reference[1]
                    else:
                        lecture['title'] = 'Pericope'

                # Argh, another ugly hack to WA my own app :(
                # Replace any unbreakable space by a regular space
                lecture['title'] = lecture['title'].replace('\xa0', ' ');

    # PASS 2: merge meargable items

    return data

# TODO: move me to a common postprocessor file
def postprocess_office_careme(version, mode, data):
    '''
    Remove "Alleluia" from introduction slide if the period is "lent"
    '''
    if data['informations'].get('temps_liturgique', '') != 'careme':
        return

    introduction_item = get_lecture_variants_by_type(data, "introduction")
    if introduction_item is not None:
        introduction_item.lectureVariants[0]['text'] = introduction_item.lectureVariants[0]['text'].replace('(Alléluia.)', '')

def postprocess_office_keys(version, mode, data):
    '''
    Postprocess office keys so that they are as compatible as possible
    with AELF's website. Special care needs to be taken. Skip this
    function when the source is not the API (ie: coming from the website)
    '''
    if data['source'] != 'api':
        return data

    for office_variant in data['variants']:
        for lecture_variants in office_variant['lectures']:
            for lecture in lecture_variants:
                key = lecture['key']
                if key.startswith('cantique'):
                    key = "office_cantique"
                elif key.startswith('psaume') and is_int(key.split('_')[-1]):
                    key = "office_%s" % key.replace('_', '')
                elif key == 'intercession':
                    # FIXME: in most offices, that's the Oraison that should become the conclusion. But that would break too much to bother
                    key = "office_conclusion"
                elif not key.startswith('office_'):
                    key = "office_%s" % key
                lecture['key'] = key

    return data

def postprocess_office_copyright(version, mode, data):
    '''
    Move the author and editor to the reference field, for crediting.
    '''
    for office_variant in data['variants']:
        for lecture_variants in office_variant['lectures']:
            for lecture in lecture_variants:
                author = lecture.get('author')
                editor = lecture.get('editor')

                if author and not editor:
                    lecture['reference'] = author
                elif editor and not author:
                    lecture['reference'] = editor
                elif editor and author:
                    lecture['reference'] = f'{author}, {editor}'

    return data

#
# Text cleaners
#

def html_fix_comments(key, soup):
    '''
    Detect and remove any HTML comments. HTML comments may just come from MS WORD copy
    and paste. They may break the processing and also increase the output size.
    '''
    comments = soup.findAll(string=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]

def html_fix_verse(key, soup):
    '''
    Detect 'font' type objects, remove all attributes, except the color.
    - red, with reference --> convert to verse reference
    - red, with text      --> keep as-is
    - not red             --> remove tag
    '''
    font_tags = soup.find_all('font') or []
    for tag in font_tags:
        # Remove all attributes, except those in whitelist
        for attr_name in list(tag.attrs.keys()):
            if attr_name not in ['color']:
                del tag[attr_name]

        # Is it red ?
        color = tag.get('color', '').lower()
        is_red = (
            (len(color) > 2 and color[0] == '#' and color[1] != '0') and
            (
                (len(color) == 4 and color[-2:] == "00") or
                (len(color) == 7 and color[-4:] == "0000")
            ))

        # Does it look like a reference ?
        if is_red and _is_verse_ref(tag.string):
            tag.name = 'span'
            tag.string = tag.string.strip()
            del tag['color']
            tag['aria-hidden'] = 'true'
            tag['class'] = 'verse'
        # Is it "just" red ? (refrain)
        elif is_red:
            tag['color'] = '#ff0000'
        else:
            # We can not unwrap as there may be nested "font" tags, and that would crash
            # one possible fix would be to search empty fonts starting from the leafs and
            # going up
            tag.attrs={}

    # Fix lecture's verses
    for tag in soup.find_all('span', class_='verse_number'):
        tag.attrs = {
            'class':       'verse',
            'aria-hidden': 'true',
        }

def html_fix_paragraph(key, soup):
    '''
    Detect paragraphs from line breaks. There should be no empty paragraphs. 2 Consecutive
    line breaks indicates a paragraph. There should be no nested paragraphs. Every <br> should
    belong to a paragraph.
    '''
    # Locate and remove orphaned <br>. A <br> is considered orphaned if it has a block
    # on both sides OR is the start / end of a block
    for tag in soup.find_all('br'):
        # TODO: support empty navigable strings

        # Remove element if it is the first
        if tag.next_sibling is None or tag.previous_sibling is None:
            tag.extract()
            continue

        # Remove element if it is only followed by br/ or last element
        sibling = tag.next_sibling
        while sibling and isinstance(sibling, Tag) and sibling.name in ['br']:
            sibling = sibling.next_sibling
        if sibling is None:
            tag.extract()
            continue

        # Remove element if it is between 2 lock elements
        for sibling in [tag.next_sibling, tag.previous_sibling]:
            if not (isinstance(sibling, Tag) and sibling.name in HTML_BLOCK_ELEMENTS):
                break
        else:
            tag.extract()

    # Ensure each text element is in a p
    node = soup.find(string=lambda text:isinstance(text, NavigableString))
    while node:
        node_next = node.find_next(string=lambda text:isinstance(text, NavigableString))
        if not str(node).strip():
            node.extract()
            node = node_next
            continue

        # Find the earliest ancestor of the element that is block element
        block_parent = node.parent
        while block_parent:
            if block_parent.name in HTML_BLOCK_ELEMENTS:
                break
            block_parent = block_parent.parent

        # Wrapped in a p, all good, move next
        if block_parent.name in 'p':
            node = node_next
            continue

        # Find the first element ancestor or element itself who has a 'p' as a
        # sibling to find the level to wrap. This is important to find the
        # appropriate wrap level: maybe this string is wrapped in a bold
        # text for example.
        node_to_wrap = node
        previous_p_sibling = None
        next_p_sibling = None

        while True:
            previous_p_sibling = node_to_wrap.find_previous_sibling("p")
            next_p_sibling = node_to_wrap.find_next_sibling("p")
            if previous_p_sibling is not None or next_p_sibling is not None or node_to_wrap.parent == block_parent:
                break
            node_to_wrap = node_to_wrap.parent

        # Create 'p' element
        new_p = soup.new_tag('p')

        # Insert the new 'p' immediately after the previous 'p' element or as
        # the first child of the parent.
        if previous_p_sibling is not None:
            previous_p_sibling.insert_after(new_p)
        else:
            block_parent.insert(0, new_p)

        # Move all elements immediately after the new 'p' to the new 'p' until the next 'p'
        for sibling in list(new_p.next_siblings):
            if sibling.name == 'p':
                continue
            sibling.extract()
            new_p.append(sibling)

        # All done :)
        node = node_next

    # Convert sequences of <br/> to <p>
    node = soup.find('br')
    while node:
        # Locate the furthest <br> element that is only linked with br, empty strings or comments
        next_br = None
        next_node = node
        while next_node:
            next_node_text = (next_node.string or "").strip(' \n\t')
            if isinstance(next_node, Tag):
                if next_node.name != 'br':
                    break
                next_br = next_node
            if isinstance(next_node, NavigableString) and next_node_text:
                break
            next_node = next_node.next_sibling

        # Get a pointer on next iteration node, while we have valid references
        next_iteration_node = next_node.find_next('br') if next_node else None

        # Build a new paragraph for all preceding elements, we have the guarantee that the parent is a p
        if next_br is not node:
            _split_node_parent(soup, 'p', node, next_br)

        # Move on
        node = next_iteration_node

    # Remove any attributes / style from paragraphs
    for p in soup.find_all('p'):
        p.attrs = {}

    # Remove empty p
    for p in soup.find_all('p'):
        if not ' '.join(p.strings).strip():
            p.extract()

def html_fix_lines(key, soup):
    '''
    Detect lines and wrap them in "<line>" tags so that we can properly wrap them
    via CSS. At this stage, we have the guarantee that all br live in a p and are
    single. Ie, there is never an empty line in a paragraph.
    '''
    CLASS_LINE={'class': ['line']}

    # Ensure each <p> contains a <line>
    for p in soup.find_all('p'):
        if p.find('span', class_="line"):
            continue
        _wrap_node_children(soup, p, 'span', **CLASS_LINE)

    # Convert <br> to <span class="line">
    node = soup.find('br')
    while node:

        # Get a pointer on next iteration node, while we have valid references
        next_iteration_node = node.find_next('br')

        # Build a new paragraph for all preceding elements, we have the guarantee that the parent is a p
        _split_node_parent(soup, 'span', node, **CLASS_LINE)

        # Move on
        node = next_iteration_node

    # Remove empty line
    for line in soup.find_all('span', class_="line"):
        if not ' '.join(line.strings).strip():
            line.extract()

    # Make line focusables
    for n, line in enumerate(soup.find_all('span', class_="line")):
        # Attributes field is shared among tag instances which causes the unique ids to be not so unique
        # hence the copy.
        line.attrs = line.attrs.copy()
        line.attrs['id'] = "%s-%s" % (key, n)
        line.attrs['tabindex'] = '0'

    # Decide if we should wrap lines
    content = soup.find('div', class_='content')
    if not content:
        return

    lines = content.find_all('span', class_="line") or []
    line_count = len(lines) or 1
    line_avg_len = 0
    line_len = 0
    for line in lines:
        string = ' '.join(line.stripped_strings)
        line_len += len(string)
    line_avg_len = float(line_len)/line_count

    # There must be at *least* 2 lines and a "good" ratio of char / line
    if line_count > 1 and line_avg_len < 70:
        for line in lines:
            line['class'] = 'line line-wrap'

def html_fix_attributes(key, soup):
    '''
    Remove all extra-attributes / simplify html
    '''
    # Ensure <u> do not have any attributes (breaks underline in the application)
    for u in soup.find_all("u"):
        u.attrs = {}


#
# Postprocessors
#

def postprocess_office_lecture_title(version, mode, key, title):
    '''
    Run all title cleaners
    '''
    if version < 30:
        return title

    title = strip_html(title)
    title = fix_case(title)
    title = fix_common_typography(title)

    return title

def postprocess_office_lecture_text(version, mode, key, text):
    '''
    Run all text cleaners
    '''
    if version < 30:
        return text

    soup = BeautifulSoup(text, 'html5lib')
    html_fix_comments(key, soup)
    html_fix_verse(key, soup)
    html_fix_paragraph(key, soup)
    html_fix_lines(key, soup)
    html_fix_attributes(key, soup)
    text = str(soup.body)[6:-7]
    text = fix_common_typography(text)
    text = fix_rv(text)

    return text

def postprocess_office_html_lecture(version, mode, lecture):
    '''
    Run all cleaners on a lecture, typically used when loading an asset which is
    supposed to be compatible with the broken AELF format.
    '''
    lecture['title'] = postprocess_office_lecture_title(version, mode, lecture['key'], lecture['title'])
    lecture['text']  = postprocess_office_lecture_text (version, mode, lecture['key'], lecture['text'])

def postprocess_office_html(version, mode, data):
    '''
    Find all office text and normalize html markup.
    '''
    for office_variant in data['variants']:
        for lecture_variants in office_variant['lectures']:
            for lecture in lecture_variants:
                postprocess_office_html_lecture(version, mode, lecture)

    return data

def postprocess_office_group_47(version, mode, data):
    '''
    Group related lectures like the antienne into the psalm
    '''
    if version < 47:
        return data

    group_related_items(data)

def postprocess_lecture_variants_group_67(version, mode, data):
    '''
    Group lecture variants
    '''
    if version < 67:
        return data

    group_lecture_variants(data)

def postprocess_antienne_67(version, mode, data):
    '''
    A group of psalms may share a common antienne. When this is the case, AELF API only
    provides a single antienne. People praying with the application expect the antienne
    to be displayed at the start of the first psalm of the series and then at the end
    of the last one.

    This function propagates the antienne to each section and inserts metadata so that
    the application knows how to render it.

    When this is the case, we assume that a single lecture variant is provided.
    '''
    if version < 67:
        return

    for office_variant in data['variants']:
        antienne = ""
        prev_lecture = None
        for lecture_variants in office_variant['lectures']:
            lecture = lecture_variants[0]
            candidate_antienne = lecture.get('antienne')

            # Mark the antienne as initial+final by default, when specified; none otherwise
            lecture['has_antienne'] = 'both' if candidate_antienne else 'none'

            # Exiting an antienne repeat section ? Reset
            if not lecture_is_psalm(lecture):
                antienne = ""
                prev_lecture = None

            # Entering an antienne repeat section ?
            elif candidate_antienne:
                antienne = candidate_antienne
                prev_lecture = lecture

            # Progressing in existing section ?
            elif antienne:
                lecture['antienne'] = antienne
                lecture['has_antienne'] = 'final'
                prev_lecture['has_antienne'] = 'initial' if prev_lecture['has_antienne'] == 'both' else 'none' # type: ignore
                prev_lecture = lecture

BOOK_CHAPTER_MATCH=re.compile(r'^(\d?\w+\d*)')
def postprocess_doxology_67(version, mode, data):
    '''
    A group of psalms may be intoned as a single continuous psalm. When this is the
    case, the doxology is only inserted when the psalm itself changes. For instance,
    when we have the following psalms 118-18, 87-I and 87-II sharing the same antienne,
    the doxology needs to be inserted after 118-18 and 87-II but not 87-I.

    Another exception is Dn 3. In this cantic, the doxology is implicit.
    '''
    if version < 67:
        return

    for office_variant in data['variants']:
        prev_lecture = None
        prev_book_chapter = None
        for lecture_variants in office_variant['lectures']:
            lecture = lecture_variants[0]
            book_chapter = None

            if match := re.search(BOOK_CHAPTER_MATCH, lecture.get('reference', '').lower().replace(' ', '')):
                book_chapter = match.group()

            if lecture.get('type') != "psaume":
                # Only psalms and cantics may have an explicit doxology. Both have type "psaume"
                lecture['has_doxology'] = False
            elif book_chapter == 'dn3':
                # Doxology is implicit in Dn 3
                lecture['has_doxology'] = False
            else:
                # Display the doxology
                lecture['has_doxology'] = True

                # Remove doxology from previous if this is a continuation AND the previous is not antienne both|final
                if prev_lecture and prev_book_chapter \
                    and prev_book_chapter == book_chapter \
                    and prev_lecture.get('has_antienne') not in ['both', 'final']:
                    prev_lecture['has_doxology'] = False

            # Move to next
            prev_lecture = lecture
            prev_book_chapter = book_chapter


VERSE_REFERENCE_MATCH=re.compile(r'\(.*\)')
def postprocess_office_title_47(version, mode, data):
    '''
    Server side title cleanup for API >= 47
    '''
    if version < 47:
        return data

    for office_variant in data['variants']:
        for lecture_variants in office_variant['lectures']:
            for lecture in lecture_variants:
                # Clean title
                lecture['title'] = re.sub(VERSE_REFERENCE_MATCH, '', lecture['title'])
                lecture['title'] = lecture['title'].replace('Pericope', 'Parole de Dieu')
                lecture['title'] = lecture['title'].replace('CANTIQUE', 'Cantique')
                if lecture['title'].startswith('Psaume'):
                    lecture['title'] = lecture['title'].replace(': ', '')

                # Prepare short / long variants
                chunks = lecture['title'].split(':', 1)
                lecture['short_title'] = chunks[0].strip()
                lecture['long_title']  = chunks[0].strip()
                if len(chunks) == 2 and chunks[1].strip() != lecture['reference'].strip():
                    lecture['long_title'] = chunks[1].strip()

    return data

def postprocess_office_pre(version, mode, data):
    '''
    Run all postprocessing, running before the office specific code
    '''
    postprocess_office_careme(version, mode, data)
    postprocess_office_keys(version, mode, data)
    postprocess_office_copyright(version, mode, data)
    postprocess_office_html(version, mode, data)
    return data

def postprocess_office_post(version, mode, data):
    '''
    Run all postprocessing, running after the office specific code
    '''
    postprocess_office_group_47(version, mode, data)
    postprocess_office_title_47(version, mode, data)
    postprocess_lecture_variants_group_67(version, mode, data)

    if data["office"] != "messes":
        postprocess_antienne_67(version, mode, data)
        postprocess_doxology_67(version, mode, data)

    return data
    
