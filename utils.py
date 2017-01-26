# -*- coding: utf-8 -*-

import os
import requests
import yaml
from keys import KEYS

AELF_RSS="https://rss.aelf.org/{day:02d}/{month:02d}/{year:02d}/{key}"
AELF_SITE="http://www.aelf.org/office-{office}?date_my={day}/{month}/{year}"
ASSET_BASE_PATH=os.path.join(os.path.abspath(os.path.dirname(__file__)), "assets")

HEADERS={'User-Agent': 'AELF - Lectures du jour - API - cathogeek@epitre.co'}
HTTP_TIMEOUT = 2 # seconds

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
    if words[0] in [u'sacré-c\u0153ur']:
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

