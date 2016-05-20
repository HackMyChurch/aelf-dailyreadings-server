# -*- coding: utf-8 -*-

import requests
from keys import KEYS

AELF_URL="http://rss.aelf.org/{day}/{month}/{year}/{key}"

# TODO: error handling
# TODO: memoization
def get_office_for_day(office, day, month, year):
    return requests.get(AELF_URL.format(day=day, month=month, year=year, key=KEYS[office])).text

def get_pronoun_for_letter(l):
    if l.lower() in [u'a', u'e', u'ê', u'é', u'è', u'i', u'o', u'u', u'y']:
        return "l'"
    else:
        return "la" # FIXME: masculin ?

