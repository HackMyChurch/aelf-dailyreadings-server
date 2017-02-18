# -*- coding: utf-8 -*-

import os
import requests
import yaml
from bs4 import BeautifulSoup
from keys import KEYS

AELF_RSS="https://rss.aelf.org/{day:02d}/{month:02d}/{year:02d}/{key}"
AELF_SITE="http://www.aelf.org/office-{office}?date_my={day}/{month}/{year}"
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

def _do_get_request(url):
    r = session.get(url, timeout=HTTP_TIMEOUT)
    if r.status_code != 200:
        raise AelfHttpError(r.status_code)
    return r.text

def get_office_for_day(office, day, month, year):
    return _do_get_request(AELF_RSS.format(day=day, month=month, year=year, key=KEYS[office]))

def get_office_for_day_aelf(office, day, month, year):
    return _do_get_request(AELF_SITE.format(office=office, day=day, month=month, year=year))

def get_office_for_day_aelf_to_rss(office, day, month, year):
    '''
    AELF has a strog tradition of being broken in creative ways. This method is yet another
    fallback on top of their unreliable RSS. It works by scrapping the web version which,
    hopefuly has a better SLA, and reformat it as RSS so that the code just does not notice.
    '''
    out = []
    data = get_office_for_day_aelf(office, day, month, year)
    soup = BeautifulSoup(data, 'html.parser')
    lectures = soup.find_all("div", class_="lecture")

    out.append(u'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <language>fr</language>
        <copyright>Copyright AELF - Tout droits réservés</copyright>
''')

    for lecture in lectures:
        # Lectures can be composed of sub-lectures. De-aggregate them
        l = {
            'title': u'',
            'text': u'',
        }
        for balise in lecture.contents + [None]:
            if balise is None or balise.name == 'h4':
                # Flush reading IF there is some content (title or text)
                if l['title'].strip() or l['text'].strip():
                    out.append(u'''
                    <item>
                        <title>{title}</title>
                        <description><![CDATA[{text}]]></description>
                    </item>'''.format(**l))

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

def lectures_soup_common_cleanup(data):
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

