# -*- coding: utf-8 -*-

import os
import requests
import yaml
from keys import KEYS

AELF_RSS="http://rss.aelf.org/{day}/{month}/{year}/{key}"
AELF_SITE="http://www.aelf.org/office-{office}?date_my={day}/{month}/{year}"
ASSET_BASE_PATH=os.path.join(os.path.abspath(os.path.dirname(__file__)), "assets")

# TODO: error handling
# TODO: memoization

def get_office_for_day(office, day, month, year):
    return requests.get(AELF_RSS.format(day=day, month=month, year=year, key=KEYS[office])).text

def get_office_for_day_aelf(office, day, month, year):
    return requests.get(AELF_SITE.format(office=office, day=day, month=month, year=year)).text

ASSET_CACHE={}
def get_asset(path):
    # Fixme: Quick n Dirty security
    if '.' in path:
        return ""

    path = os.path.join(ASSET_BASE_PATH, path+".yaml")

    with open(path) as f:
        return yaml.load(f)

def get_pronoun_for_letter(l):
    if l.lower() in [u'a', u'e', u'ê', u'é', u'è', u'i', u'o', u'u', u'y']:
        return "l'"
    else:
        return "la" # FIXME: masculin ?

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

