# -*- coding: utf-8 -*-

import os
import requests
import yaml
import re
from bs4 import BeautifulSoup
from keys import KEYS
from collections import OrderedDict

AELF_JSON="https://api.aelf.org/v1/{office}/{year:04d}-{month:02d}-{day:02d}"
AELF_RSS="https://rss.aelf.org/{day:02d}/{month:02d}/{year:02d}/{key}"
AELF_SITE="http://www.aelf.org/{year:04d}-{month:02d}-{day:02d}/romain/{office}"
ASSET_BASE_PATH=os.path.join(os.path.abspath(os.path.dirname(__file__)), "assets")

HEADERS={'User-Agent': 'AELF - Lectures du jour - API - cathogeek@epitre.co'}
HTTP_TIMEOUT = 10 # seconds

# TODO: memoization

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

PSALM_MATCH=re.compile('^[0-9]+(-[IV0-9]+)?$')
def is_psalm_ref(data):
    return re.match(PSALM_MATCH, data.replace(' ', ''))

def _id_to_title(data):
    '''
    Forge a decent title from and ID as a fallbackd when the API does not provide a title
    '''
    chunks = data.split('_')
    try:
        int(chunks[-1])
    except:
        pass
    else:
        chunks.pop()
    return (u' '.join(chunks)).capitalize()

def _do_get_request(url):
    r = session.get(url, timeout=HTTP_TIMEOUT)
    if r.status_code != 200:
        raise AelfHttpError(r.status_code)
    return r

def get_office_for_day(office, day, month, year):
    return _do_get_request(AELF_RSS.format(day=day, month=month, year=year, key=KEYS[office])).text

def get_office_for_day_aelf(office, day, month, year):
    return _do_get_request(AELF_SITE.format(office=office, day=day, month=month, year=year)).text

def get_office_for_day_api(office, day, month, year):
    '''
    Grab data from api.aelf.org and format it in a consistent way. This api is very creative in
    mixing different conventions in a single file. Output from the function is guaranteed to be
    consistent as far as the format is concerned, but is not yet post-proceced. You'll probably
    want to merge some readings befor sending.
    '''
    data = _do_get_request(AELF_JSON.format(office=office, day=day, month=month, year=year)).json(object_pairs_hook=OrderedDict)

    # Start to build our json format from API's format
    out = {
        u'informations': postprocess_informations(dict(data.pop('informations'))),
        u'lectures': {},
    }

    # 'information' office has no reading
    # FIXME: in the future, we'll get informations through "mass" only, and this case should move
    #        compat API should use it and postprocess informations for each office
    if not data:
        return out

    # Move from a list or single item to a dict VARIANT => LECTURES
    name, lectures = data.items().pop()
    if isinstance(lectures, list):
        # In this case, everything is a list
        cleaned = {}
        for variant in lectures:
            cleaned[variant['nom']] = OrderedDict((o['type'], o) for o in variant['lectures'])
        lectures = cleaned
    else:
        lectures = {name: lectures}

    # Iterate on all variants / lectures to normalize
    for variant_name, variant in lectures.iteritems():
        out['lectures'][variant_name] = []

        # In the lectures office, the patristique text is... broken
        patristique = {
            u'titre': '',
            u'texte': '',
        }
        for name, lecture in variant.iteritems():
            # There is not point in attempting to parse empty data: will fail anyway
            if not name or not lecture:
                continue

            if office == "messes":
                # WIP: this is still very much broken
                titre = _id_to_title(name)
                number = name.rsplit('_', 1)[-1]
                if is_int(number):
                    if number == '1':
                        titre = u"1ère %s" % titre
                    else:
                        titre = u"%sème %s" % (number, titre)

                if lecture['titre']:
                    titre = '%s : %s' % (titre, lecture['titre'])

                lecture = {
                    'titre':     titre,
                    'reference': lecture['ref'],
                    'texte':     lecture['contenu'],
                }
            # Value may not be a dict
            if isinstance(lecture, basestring):
                # Re-assemble patristique text...
                if name == 'titre_patristique':
                    patristique['titre'] = 'Lecture patristique: %s' % lecture
                    continue
                elif name == 'texte_patristique':
                    patristique['texte'] = lecture
                    name = 'lecture_patristique'
                    lecture = patristique
                else:
                    # Broken, general case...
                    lecture = {
                        'texte': lecture,
                    }

            # Now, lecture is a dict. Not yet a consistent one, but a dict
            cleaned = {
                u'title':     lecture.get('titre',     ''),
                u'reference': lecture.get('reference', ''),
                u'text':      lecture.get('texte',     ''),
                u'key':       name,
            }

            # Title cleanup / compat with current applications
            # FIXME: move this crap to the common cleanup path once it is compatible with the dict
            if cleaned['title']:
                if name in ["hymne", "pericope", "lecture", "lecture_patristique"]:
                    if not cleaned['title'][0] in [u'«', u"'", u'"']:
                        cleaned['title'] = u"« %s »" % cleaned['title']
                    cleaned['title'] = u"%s : %s" % (_id_to_title(name), cleaned['title'])
            else:
                cleaned['title'] = _id_to_title(name)

            if cleaned['reference']:
                if cleaned['reference'].lower().startswith('cf.'):
                    cleaned['reference'] = cleaned['reference'][3:]

                if 'cantique' in cleaned['reference'].lower():
                    cleaned['title'] = cleaned['reference']
                    if '(' in cleaned['reference']:
                        cleaned['reference'] = cleaned['reference'].split('(')[1].split(')')[0]
                elif cleaned['title'] in "Pericope":
                    cleaned['title'] = "%s : %s" % (cleaned['title'], cleaned['reference'])
                elif cleaned['title'] == "Psaume" and is_psalm_ref(cleaned['reference']):
                    cleaned['title'] = "%s : %s" % (cleaned['title'], cleaned['reference'].replace(' ', ''))
                else:
                    cleaned['title'] = "%s (%s)" % (cleaned['title'], cleaned['reference'])

            if name.split('_', 1)[0] in ['verset']:
                cleaned['title'] = 'verset'

            out['lectures'][variant_name].append(cleaned)

    return out

def get_office_for_day_aelf_json(office, day, month, year):
    '''
    AELF has a strog tradition of being broken in creative ways. This method is yet another
    fallback on top of their unreliable RSS. It works by scrapping the web version which,
    hopefuly has a better SLA, and reformat it using the same format as ``get_office_for_day_api``
    '''
    data = get_office_for_day_aelf(office, day, month, year)
    soup = BeautifulSoup(data, 'html.parser')
    lectures = soup.find_all("div", class_="lecture")
    variant_titles = [title.string.capitalize() for title in soup.find_all('h1')]
    variant_current = -1
    variant_current_str = ''

    if not variant_titles:
        variant_titles = [office.capitalize()]

    # Start to build our json format from API's format
    out = {
        u'informations': {}, # TODO...
        u'lectures': {},
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

        # Load or create the variant if need be
        if variant_name not in out[lectures]:
            out[lectures] = []
        variant = out[lectures]

        # Lectures can be composed of sub-lectures. De-aggregate them
        lecture_key = variant_key.rsplit('_', 1)[-1] if '_' in variant_key else u''
        l = {
            u'title':     u'',
            u'text':      u'',
        }
        for balise in lecture.contents + [None]:
            if balise is None or balise.name == 'h4':
                # Flush reading IF there is some content (title or text)
                if l['title'].strip() or l['text'].strip():
                    variant.append({
                        u'title':     l['title'],
                        u'text':      l['text'],
                        u'reference': u'', # TODO
                        u'key':       lecture_key,
                    })

            if balise is None:
                # This is a hack to share flush path. I'm in a hurry. AELF is one again broken.
                break

            if balise.name == 'h4':
                # Next reading
                l['title'] = lecture.h4.extract().text.strip()
                l['text'] = u''
            else:
                # Reading content
                l['text'] += unicode(balise)

def json_to_rss(data):
    '''
    API and json scrappers return a json of the form:
    ```json
    {
        "informations": {},
        "lectures": {
            "OFFICE_NAME": [
                {
                    "title":     "",
                    "reference": "",
                    "text":      "",
                    "key":       "",
                },
            ],
            "OFFICE_VARIANTE_NAME": []
        }
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
        <source>website</source>
        <copyright>Copyright AELF - Tout droits réservés</copyright>
''')

    for office, lectures in data.get('lectures', {}).iteritems():
        for lecture in lectures:
            out.append(u'''
            <item>
                <variant>{office}</variant>
                <title>{title}</title>
                <reference>{reference}</reference>
                <key>{reference}</key>
                <description><![CDATA[{text}]]></description>
            </item>'''.format(office=office, **lecture))

    out.append(u'''</channel></rss>''')
    return u''.join(out)

def get_office_for_day_api_rss(office, day, month, year):
    '''
    Get office from new API but return it as RSS so that we do not need to change the full stack at once
    '''
    data = get_office_for_day_api(office, day, month, year)
    rss = json_to_rss(data)
    return lectures_soup_common_cleanup(rss)

def get_office_for_day_aelf_rss(office, day, month, year):
    data = get_office_for_day_aelf_json(office, day, month, year)
    rss = json_to_rss(data)
    return lectures_soup_common_cleanup(rss)

ASSET_CACHE={}
def get_asset(path):
    # Fixme: Quick n Dirty security
    if '.' in path:
        return ""

    path = os.path.join(ASSET_BASE_PATH, path+".yaml")

    with open(path) as f:
        return yaml.load(f)

def get_pronoun_for_sentence(sentence):
    words = [w.lower() for w in sentence.split(" ")]

    # Argh, hard coded exception
    if words[0] in ['saint', 'sainte'] and u"trinité" not in sentence:
        return ''

    # Already a determinant or equivalent
    if words[0] in ['l\'', 'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'd\'']:
        return ''

    # If it starts by a vowel, that's easy, don't care about M/F
    if words[0][0] in [u'a', u'e', u'ê', u'é', u'è', u'i', u'o', u'u', u'y']:
        return "l'"

    # Attempt to guess M/F by checking if 1st words ends with 'e'. Default on F
    if words[0] in [u'sacré-c\u0153ur', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']:
        return u"le "

    return u"la "

def get_item_by_title_internal(items, title, normalize):
    '''Get first item containing 'title' in its title if any. Normalize input.'''
    title = normalize(title)
    for item in items:
        if title in normalize(item.title.text):
            return item
    return None

def get_item_by_title(items, title):
    '''Get first item containing 'title' in its title if any. Case insensitive.'''
    return get_item_by_title_internal(items, title, lambda x: x.strip().lower())

def _filter_fete(fete):
    '''fete can be proceesed from 2 places. Share common filtering code'''
    fete = re.sub(r'(\w)(S\.|St|Ste) ', r'\1, \2 ', fete) # Fix word splitting when multiple Saints
    return fete.replace("S. ", "Saint ")\
               .replace("St ", "Saint ")\
               .replace("Ste ", "Sainte ")

def postprocess_informations(informations):
    '''
    Generate 'text' key in an information dict from json API
    '''
    text = u""
    fete_done = False
    fete_skip = False

    # Never print fete if this is the semaine
    if informations.get('fete', '').split(' ')[0] == informations.get('semaine', '').split(' ')[0]:
        fete_skip = True

    if 'jour' in informations:
        text += informations['jour']
        if not fete_skip and 'fete' in informations:
            fete = _filter_fete(informations['fete'])

            # Single word (paque, ascension, noel, ...)
            if fete and ' ' not in fete:
                pronoun = get_pronoun_for_sentence(fete)
                text += u" de %s%s" % (pronoun, fete)
                fete_done = True
            # De la férie
            elif u'férie' in fete:
                text += u" " + fete
                fete_done = True
    if 'semaine' in informations:
        if text:
            text += u', '
        semaine =  informations['semaine']
        text += semaine

        numero = re.match('^[0-9]*', semaine).group()
        numero = ((int(numero)-1) % 4) + 1 if numero else ""
        semaines = {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}
        if numero in semaines:
            text += " (semaine %s du psautier)" % semaines[numero]

    if 'annee' in informations:
        if text:
            if fete_done:
                text += u", année %s" % informations['annee']
            else:
                text += u" de l'année %s" % informations['annee']
        else:
            text += u"Année %s" % informations['annee']

    if text:
        text += "."

    if not fete_skip and not fete_done and 'fete' in informations and ('jour' not in informations or informations['jour'] not in informations['fete']):
        fete = _filter_fete(informations['fete'])
        verbe = u"fêtons" if u'saint' in fete.lower() else u"célèbrons"

        # Single word (paque, ascension, noel, ...)
        if fete and ' ' not in fete:
            text += u" Nous %s %s." % (verbe, fete)
        # Standard fete
        if fete and u'férie' not in fete:
            pronoun = get_pronoun_for_sentence(fete)
            text += u' Nous %s %s%s.' % (verbe, pronoun, fete)

    if 'couleur' in informations:
        text += u" La couleur liturgique est le %s." % informations['couleur']

    # Final cleanup: 1er, 1ère, 2ème, 2nd, ... --> exposant
    text = re.sub(ur'([0-9])(er|nd|ère|ème) ', r'\1<sup>\2</sup> ', text)
    text = text[:1].upper() + text[1:]

    # Inject text
    informations['text'] = text
    return informations

def lectures_soup_common_cleanup(data):
    # TODO: move to json
    soup = BeautifulSoup(data, 'html.parser')
    items = soup.find_all('item')

    # Fix titles for compat with older applications
    for item in items:
        # FIXME: this hack is plain Ugly and there only to make newer API regress enough to be compatible with deployed applications
        title = item.title
        title_sig = title.string.strip().lower()
        if title_sig.split(u' ')[0] in [u'antienne']:
            title.string = 'antienne'
        elif title_sig.split(u' ')[0] in [u'repons', u'répons']:
            title.string = 'repons'
        elif title_sig.startswith('parole de dieu'):
            reference = title.string.rsplit(':', 1)
            if len(reference) > 1:
                title.string = 'Pericope : (%s)' % reference[1]
            else:
                title.string = 'Pericope'

        # Argh, another ugly hack to WA my own app :(
        # Replace any unbreakable space by a regular space
        title.string = title.string.replace(u'\xa0', u' ');

    return soup.prettify()

