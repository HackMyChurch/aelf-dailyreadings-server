# -*- coding: utf-8 -*-

import os
import requests
import yaml
import re
from bs4 import BeautifulSoup
from keys import KEYS
from xml.sax.saxutils import escape
from collections import OrderedDict, namedtuple

AELF_JSON="https://api.aelf.org/v1/{office}/{year:04d}-{month:02d}-{day:02d}"
AELF_SITE="http://www.aelf.org/{year:04d}-{month:02d}-{day:02d}/romain/{office}"
EPITRE_CO_JSON="http://epitre.co/api/1.0/ref/fr-lit/{reference}"
ASSET_BASE_PATH=os.path.join(os.path.abspath(os.path.dirname(__file__)), "assets")

HEADERS={'User-Agent': 'AELF - Lectures du jour - API - cathogeek@epitre.co'}
HTTP_TIMEOUT = 10 # seconds

OFFICE_NAME = {
    "messes": "messe",
}

# TODO: memoization
# TODO: rewrite as a class

# Create some base, internal types
LecturePosition = namedtuple('LecturePosition', ['variantIdx', 'lectureIdx', 'lecture'])

class AelfHttpError(Exception):
    def __init__(self, status, message=None):
        super(AelfHttpError, self).__init__(message)
        self.status = status

# Create a connection pool
session = requests.Session()
session.headers.update(HEADERS)

def is_int(data):
    try:
        int(data)
    except:
        return False
    return True

def is_letter(data):
    if not data:
        return False

    for c in data.lower():
        if ord(c) < ord('a') or ord(c) > ord('z'):
            return False
    return True

PSALM_MATCH=re.compile('^[0-9]+(-[IV0-9]+)?$')
def is_psalm_ref(data):
    return re.match(PSALM_MATCH, data.replace(' ', ''))

def extract_title_reference(title):
    title = title.strip(' \t\n\r')
    chunks = title.split('(', 1)
    title = chunks[0]
    if len(chunks) < 2:
        return title, ""

    reference = chunks[1].rsplit(')', 1)[0]
    return title, reference

ID_TO_TITLE = {
    'benediction': u'Bénédiction',
}

def _id_to_title(data):
    '''
    Forge a decent title from and ID as a fallbackd when the API does not provide a title
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
    return (u' '.join(chunks)).capitalize()

# FIXME: this is very hackish. We'll need to replace this with a real parser
def clean_ref(ref):
    ref = ref.strip()

    # Remove any leading 'cf.'
    if ref.lower().startswith('cf.'):
        ref = ref[3:].lstrip()

    if not ref:
        return ref

    # Add 'Ps' if missing
    chunks = ref.split(' ')
    if is_letter(chunks[0]) or (len(chunks) > 1 and is_letter(chunks[1])):
        return ref

    return 'Ps %s' % ref

def _do_get_request(url):
    r = session.get(url, timeout=HTTP_TIMEOUT)
    if r.status_code != 200:
        raise AelfHttpError(r.status_code)
    return r

def get_office_for_day_aelf(office, date):
    return _do_get_request(AELF_SITE.format(office=office, day=date.day, month=date.month, year=date.year)).text

def get_lecture_text_from_epitre(reference):
    reference = reference.replace(' ', '')
    if not reference:
        return ""

    r = _do_get_request(EPITRE_CO_JSON.format(reference=reference))
    data = r.json().get('data', {})
    out = []
    multiple_chapters = ';' in reference
    for verse in data.get('verse', []):
        reference = '%s.%s' % (verse[0], verse[1]) if multiple_chapters else verse[1]
        out.append('<font color="#FF0000" size="1">%s</font>%s' % (reference, verse[2]))

    return '<br/>'.join(out)

def get_office_for_day_api(office, date):
    '''
    Grab data from api.aelf.org and format it in a consistent way. This api is very creative in
    mixing different conventions in a single file. Output from the function is guaranteed to be
    consistent as far as the format is concerned, but is not yet post-proceced. You'll probably
    want to merge some readings befor sending.
    '''
    data = _do_get_request(AELF_JSON.format(office=office, day=date.day, month=date.month, year=date.year)).json(object_pairs_hook=OrderedDict)

    # Start to build our json format from API's format
    out = {
        u'informations': dict(data.pop('informations')),
        u'variants': [],
        u'source': 'api',
        u'office': office,
        u'date': date.isoformat(),
    }

    # 'information' office has no reading
    # FIXME: in the future, we'll get informations through "mass" only, and this case should move
    #        compat API should use it and postprocess informations for each office
    if not data:
        return lectures_common_cleanup(out)

    # PASS 1: Normalize data to a list of office variantes. Each variant is a list of offices with a type
    # we use lists to 1/ preserve order 2/ allow for duplicates like "short version"
    name, variants = data.items().pop()
    if isinstance(variants, list):
        # Mass: multiple variants, lectures list inside, possible collision on types
        counter = 0; # We'll need it to generate variants name in case it's missing
        cleaned = []
        for variant in variants:
            # Yes, it appends (cf Rameaux)
            if not variant['lectures']:
                continue

            # Handle variants with missing name (cf Rameaux)
            counter += 1
            if not variant['nom']:
                variant['nom'] = "%s %s" % (OFFICE_NAME.get(office, office).capitalize(), counter)

            cleaned.append(variant)
        variants = cleaned
    else:
        # Regular Office: single variant, type --> lecture dict inside
        lectures = []

        # In the lectures office, the patristique text is... broken
        patristique = {
            u'titre': '',
            u'texte': '',
        }

        for name, lecture in variants.iteritems():
            # 'lecture' may not be a dict yet...
            if isinstance(lecture, basestring):
                # Re-assemble patristique text...
                if name == 'titre_patristique':
                    patristique['titre'] = u'Lecture patristique: %s' % lecture
                    continue
                elif name == 'texte_patristique':
                    patristique['texte'] = lecture
                    name = u'lecture_patristique'
                    lecture = patristique
                else:
                    # Broken, general case...
                    lecture = {
                        'texte': lecture,
                    }
            if isinstance(lecture, dict):
                lecture = dict(lecture) # Drop the OrderedDict overhead, no longer needed
                lecture['type'] = name
                lectures.append(lecture)
            # At this stage, we only have valid looking data in the dict
            # Te Deum being an empty list, it's also been skipped. That's
            # OK, we'll add it later

        variants = [
            {
                'nom':      OFFICE_NAME.get(office, office).capitalize(),
                'lectures': lectures,
            }
        ]

    # PASS 2: Normalize all items
    for variant in variants:
        variant_name = variant['nom']
        out_variant = {
            'name':     variant_name,
            'lectures': [],
        }
        out['variants'].append(out_variant)
        for lecture in variant['lectures']:
            name = lecture.get('type', '')

            if office == "messes":
                # WIP: this is still very much broken
                # TODO: move somewhere else. This approach downgrades the data...
                titre = _id_to_title(name)
                number = name.rsplit('_', 1)[-1]
                if is_int(number):
                    if number == '1':
                        titre = u"1ère %s" % titre
                    else:
                        titre = u"%sème %s" % (number, titre)

                if lecture['titre']:
                    titre = u'%s : %s' % (titre, lecture['titre'])

                texte = []

                intro       = lecture.get('intro_lue',         '').strip()
                refrain     = lecture.get('refrain_psalmique', '').strip()
                refrain_ref = lecture.get('ref_refrain',       '').strip()
                verset      = lecture.get('verset_evangile',   '').strip()
                verset_ref  = lecture.get('ref_verset',        '').strip()
                contenu     = lecture.get('contenu',           '').strip()

                if intro:
                    texte.append(u'<b><i>%s</i></b>' % intro)

                if refrain:
                    texte.append(u'<font color="#CC0000">R/ %s</font>' % refrain)

                if verset:
                    verset = verset.strip()
                    if verset.startswith('<p>'): verset = verset[3:]
                    if verset.endswith('<p>'):   verset = verset[:-4]
                    texte.append(u'<blockquote><b>Acclamation&nbsp;:</b><br/>%s<small><i>— %s</i></small></blockquote>' % (verset, clean_ref(verset_ref)))

                if contenu:
                    texte.append(contenu)

                lecture = {
                    'titre':     titre,
                    'reference': lecture['ref'],
                    'texte':     u''.join(texte),
                }

            # Now, lecture is a dict. Not yet a consistent one, but a dict
            cleaned = {
                u'title':     lecture.get('titre',     ''),
                u'reference': lecture.get('reference', ''),
                u'text':      lecture.get('texte',     ''),
                u'key':       name,
            }

            out_variant['lectures'].append(cleaned)

    return lectures_common_cleanup(out)

LAST = object()
def get_office_for_day_aelf_json(office, date):
    '''
    This is an alternative method to the API to get the offices. It works by scrapping
    the website and returning the same internal format as the API.
    This method is also used as a fallback in case a lecture or full office is missing
    '''
    data = get_office_for_day_aelf(office, date)
    soup = BeautifulSoup(data, 'html5lib')
    lectures = soup.find_all("div", class_="lecture")
    variant_titles = [title.string.capitalize() for title in soup.find_all('h1')]
    variant_current = -1
    variant_current_str = ''

    if not variant_titles:
        variant_titles = [office.capitalize()]

    # Start to build our json format from API's format
    out = {
        u'informations': {}, # TODO...
        u'variants': [],
        u'source': 'website',
        u'office': office,
        u'date': date.isoformat(),
    }

    for lecture in lectures:
        # Compute the variant id, go to next variant if needed
        lecture_key = lecture.attrs.get('id', office)
        variant_key = lecture_key.split('_', 1)[0]
        if variant_key != variant_current_str:
            variant_current += 1
            variant_current_str = variant_key

        # Compute the name of the variant
        if variant_current >= len(variant_titles):
            variant_name = office.capitalize()
            if variant_current > 0:
                variant_name  = "%s %d" % (variant_name, variant_current)
        else:
            variant_name = variant_titles[variant_current]

        # Is it the last known variant or do we need to create a new one ?
        if out['variants'] and out['variants'][-1]['name'] == variant_name:
            variant = out['variants'][-1]
        else:
            variant = {
                'name': variant_name,
                'lectures': [],
            }
            out['variants'].append(variant)

        # Lectures can be composed of sub-lectures. De-aggregate them
        l = {
            u'title':     u'',
            u'text':      u'',
        }
        for balise in lecture.contents + [LAST]:
            if balise == LAST or balise.name == 'h4':
                # Flush reading IF there is some content (title or text)
                if l['title'].strip() or l['text'].strip():
                    title, reference =  extract_title_reference(l['title'].strip(' \t\n\r'))
                    text  =  l['text'].strip(' \t\n\r')
                    variant['lectures'].append({
                        u'title':     title,
                        u'text':      text,
                        u'reference': reference,
                        u'key':       lecture_key,
                    })

            if balise is LAST:
                # This is a hack to share flush path. I'm in a hurry. AELF is one again broken.
                break

            if balise.name == 'h4':
                # Next reading
                l['title'] = lecture.h4.extract().text.strip()
                l['text'] = u''
            else:
                # Reading content
                l['text'] += unicode(balise)

    # All done!
    return lectures_common_cleanup(out)

def json_to_rss(data):
    '''
    API and json scrappers return a json of the form:
    ```json
    {
        "informations": {},
        "variants": [
            {
                "name": OFFICE_NAME,
                "lectures": [
                    {
                        "title":     "",
                        "reference": "",
                        "text":      "",
                        "key":       "",
                    },
                ],
            },
            {
                "name": OFFICE_VARIANTE_NAME,
                "lectures": []
            }
        ]
    }
    ```

    When multiple alternatives are proposed for an office (typically the mass), chain them and
    add a <variant> with the "OFFICE_NAME" key in the items
    '''
    out = []
    out.append(u'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <language>fr</language>
        <source>%s</source>
        <copyright>Copyright AELF - Tout droits réservés</copyright>
''' % data.get('source', 'unk'))

    for variant in data.get('variants', []):
        office   = variant['name']
        lectures = variant['lectures']
        for lecture in lectures:
            out.append(u'''
            <item>
                <variant>{office}</variant>
                <title>{title}</title>
                <reference>{reference}</reference>
                <key>{key}</key>
                <description><![CDATA[{text}]]></description>
            </item>'''.format(
                office    = office,
                title     = escape(lecture.get('title', '')),
                reference = escape(lecture.get('reference', '')),
                key       = escape(lecture.get('key', '')),
                text      = lecture.get('text', ''),
            ))

    out.append(u'''</channel></rss>''')
    return u''.join(out)

ASSET_CACHE={}
def get_asset(path):
    # Fixme: Quick n Dirty security
    if '.' in path:
        return ""

    path = os.path.join(ASSET_BASE_PATH, path+".yaml")

    with open(path) as f:
        return yaml.load(f)


DETERMINANTS = ['l\'', 'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'd\'', 'au', u'à'];
def fix_case(sentence):
    words = sentence.split(' ')
    cleaned = []
    for word in words:
        if not word:
            continue
        c = word[0]
        word = word.lower()
        if c != word[0] and word not in DETERMINANTS:
            word = word.capitalize()
        cleaned.append(word)
    return ' '.join(cleaned)

def get_pronoun_for_sentence(sentence):
    words = [w.lower() for w in sentence.split(" ")]

    # Argh, hard coded exception
    if words[0] in ['saint', 'sainte'] and u"trinité" not in sentence:
        return ''

    # Already a determinant or equivalent
    if words[0] in DETERMINANTS:
        return ''

    # If it starts by a vowel, that's easy, don't care about M/F
    if words[0][0] in [u'a', u'e', u'ê', u'é', u'è', u'i', u'o', u'u', u'y']:
        return "l'"

    # Attempt to guess M/F by checking if 1st words ends with 'e'. Default on F
    if words[0] in [u'sacré-c\u0153ur', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']:
        return u"le "

    return u"la "

# FIXME: this function is deprecated (use json accessors instead)
def get_item_by_title_internal(items, title, normalize):
    '''Get first item containing 'title' in its title if any. Normalize input.'''
    title = normalize(title)
    for item in items:
        if title in normalize(item.title.text):
            return item
    return None

# FIXME: this function is deprecated (use json accessors instead)
def get_item_by_title(items, title):
    '''Get first item containing 'title' in its title if any. Case insensitive.'''
    return get_item_by_title_internal(items, title, lambda x: x.strip().lower())

def get_lectures_by_type(data, name):
    '''
    Find all lectures of type ``name``. Return a list of ``(variant_idx, lecture_idx, lecture)``
    '''
    out = []
    for variant_idx, variant in enumerate(data['variants']):
        for lecture_idx, lecture in enumerate(variant['lectures']):
            if lecture['key'] == name:
                out.append(LecturePosition(variant_idx, lecture_idx, lecture))
    return out

def get_lecture_by_type(data, name):
    '''
    Find first lecture element with type ``name`` or return None
    '''
    lectures = get_lectures_by_type(data, name)
    if lectures:
        return lectures[0]
    return None

def insert_lecture_before(data, lecture, before):
    '''
    Insert raw ``lecture`` dict before ``before`` LecturePosition object
    '''
    data['variants'][before.variantIdx]['lectures'].insert(before.lectureIdx, lecture)

def insert_lecture_after(data, lecture, after):
    '''
    Insert raw ``lecture`` dict after ``after`` LecturePosition object
    '''
    data['variants'][after.variantIdx]['lectures'].insert(after.lectureIdx+1, lecture)

def _filter_fete(fete):
    '''fete can be proceesed from 2 places. Share common filtering code'''
    fete = fete.strip()
    fete = re.sub(r'(\w)(S\.|St|Ste) ', r'\1, \2 ', fete) # Fix word splitting when multiple Saints
    fete = fete.replace("S. ", "Saint ")\
               .replace("St ", "Saint ")\
               .replace("Ste ", "Sainte ")

    verbe = u"fêtons" if u'saint' in fete.lower() else u"célèbrons"
    text = ''

    # Single word (paque, ascension, noel, ...)
    if fete and ' ' not in fete and fete.lower() not in [u'ascension', u'pentecôte']:
        text += u" Nous %s %s" % (verbe, fete)
    # Standard fete
    elif fete and u'férie' not in fete:
        pronoun = get_pronoun_for_sentence(fete)
        text += u' Nous %s %s%s' % (verbe, pronoun, fete)
    else:
        text += fete

    return text

def postprocess_informations(informations):
    '''
    Generate 'text' key in an information dict from json API
    '''
    text = u""
    fete_skip = False
    jour_lit_skip = False

    if 'fete' not in informations:
        informations['fete'] = u''

    # Never print fete if this is the semaine
    if informations.get('jour_liturgique_nom', '').split(' ')[0] == informations.get('semaine', '').split(' ')[0]:
        jour_lit_skip = True
    if informations.get('jour_liturgique_nom', '') == informations.get('fete', '') and u'férie' not in informations.get('fete', ''):
        jour_lit_skip = True
    if informations['fete'] == informations.get('degre', ''):
        fete_skip = True

    if not jour_lit_skip and 'jour_liturgique_nom' in informations and u'férie' not in informations.get('jour_liturgique_nom', ''):
        text += _filter_fete(informations['jour_liturgique_nom'])
    elif 'jour' in informations:
        text += informations['jour'].strip()
        if not jour_lit_skip and 'jour_liturgique_nom' in informations:
            text += ' %s' % _filter_fete(informations['jour_liturgique_nom'])

    if 'semaine' in informations:
        semaine = informations['semaine']
        if text:
            text += u', '
        text += semaine

        numero = re.match('^[0-9]*', semaine).group()
        numero = ((int(numero)-1) % 4) + 1 if numero else ""
        semaines = {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}
        if numero in semaines:
            text += " (semaine %s du psautier)" % semaines[numero]

    if 'annee' in informations:
        if text:
            text += u" de l'année %s" % informations['annee']
        else:
            text += u"Année %s" % informations['annee']

    if text:
        text += "."

    if not fete_skip and 'fete' in informations and ('jour' not in informations or informations['jour'] not in informations['fete']):
        fete = _filter_fete(informations['fete'])
        if fete and not u'férie' in fete:
            text += "%s." % fete

    if 'couleur' in informations:
        text += u" La couleur liturgique est le %s." % informations['couleur']

    # Final cleanup: 1er, 1ère, 2ème, 2nd, ... --> exposant
    text = re.sub(ur'([0-9])(er|nd|ère|ème) ', r'\1<sup>\2</sup> ', text)
    text = text[:1].upper() + text[1:]

    # Inject text
    informations['text'] = text
    return informations

def lectures_common_cleanup(data):
    '''
    Walk on the variants and lectures lists and apply common cleanup code. This is where
    most of the current application's cleanup logic will migrate. In the mean time, filter
    the json to reproduce the old RSS API bugs (YEAH!)
    '''
    data['informations'] = postprocess_informations(data['informations'])

    # PASS 1: post-process lectures items
    for variant in data['variants']:
        for lecture in variant['lectures']:
            # Title cleanup / compat with current applications
            name = lecture['key']
            if lecture['title']:
                if name in ["hymne", "pericope", "lecture", "lecture_patristique"]:
                    if not lecture['title'][0] in [u'«', u"'", u'"']:
                        lecture['title'] = u"« %s »" % lecture['title']
                    lecture['title'] = u"%s : %s" % (_id_to_title(name), lecture['title'])
            else:
                lecture['title'] = _id_to_title(name)

            if lecture['reference']:
                raw_ref = lecture['reference']
                lecture['reference'] = clean_ref(raw_ref)

                if 'cantique' in lecture['reference'].lower():
                    lecture['title'] = lecture['reference']
                    if '(' in lecture['reference']:
                        lecture['reference'] = lecture['reference'].split('(')[1].split(')')[0]
                elif lecture['title'] in "Pericope":
                    lecture['title'] = u"%s : %s" % (lecture['title'], lecture['reference'])
                elif lecture['title'] == "Psaume" and is_psalm_ref(raw_ref):
                    lecture['title'] = u"%s : %s" % (lecture['title'], raw_ref)
                else:
                    lecture['title'] = u"%s (%s)" % (lecture['title'], lecture['reference'])

            if name.split('_', 1)[0] in ['verset']:
                lecture['title'] = u'verset'

            # FIXME: this hack is plain Ugly and there only to make newer API regress enough to be compatible with deployed applications
            title_sig = lecture['title'].strip().lower()
            if title_sig.split(u' ')[0] in [u'antienne']:
                lecture['title'] = 'antienne'
            elif title_sig.split(u' ')[0] in [u'repons', u'répons']:
                lecture['title'] = 'repons'
            elif title_sig.startswith('parole de dieu'):
                reference = lecture['title'].rsplit(':', 1)
                if len(reference) > 1:
                    lecture['title'] = 'Pericope : (%s)' % reference[1]
                else:
                    lecture['title'] = 'Pericope'

            # Argh, another ugly hack to WA my own app :(
            # Replace any unbreakable space by a regular space
            lecture['title'] = lecture['title'].replace(u'\xa0', u' ');

    # PASS 2: merge meargable items

    return data

