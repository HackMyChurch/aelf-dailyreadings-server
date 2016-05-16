#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Response, abort
app = Flask(__name__)

import re
import requests
from bs4 import BeautifulSoup
from keys import KEYS

AELF_URL="http://rss.aelf.org/{day}/{month}/{year}/{key}"

# TODO: error handling
# TODO: memoization
def get_office_for_day(office, day, month, year):
    return requests.get(AELF_URL.format(day=day, month=month, year=year, key=KEYS[office])).text

# TODO: memoization
def office_meta_postprocess(data):
    soup = BeautifulSoup(data, 'xml')
    items = soup.find_all('item')
    kv = {}

    # Use first element as a template
    template = items[0]

    # Get data and remove all elements from tree
    for item in items:
        item.extract()
        title, description = item.title.text.strip(), item.description.text.strip()
        if title and description:
            kv[title] = description

    # Build new element
    template.title.string = "Jour liturgique"
    template.description.string = ""

    description = u""
    if 'jour' in kv:
        description += kv['jour']
    if 'fete' in kv and ('jour' not in kv or kv['jour'] not in kv['fete']):
        fete = re.sub(r'(\w)(S\.|Ste) ', r'\1, \2 ', kv['fete']) # Fix word splitting when multiple Saints
        if description:
            if ' ' not in fete:
                if kv['fete'][0].lower() in [u'a', u'e', u'ê', u'é', u'è', u'i', u'o', u'u', u'y']:
                    description += " de l'"
                else:
                    description += " de la " # FIXME: masculin ?
            elif u'férie' in fete:
                description += u" "
            else:
                description += u", "
        description += fete
    if 'semaine' in kv:
        if description:
            description += u', '
        description += kv['semaine']
    if 'annee' in kv:
        if kv.get("degre", u"") == u'Solennité du Seigneur':
            description += u", année %s" % kv['annee']
        elif description:
            description += u" de l'année %s" % kv['annee']
        else:
            description += u"Année %s" % kv['annee']
    if 'couleur' in kv:
        if description:
            description += u". "
        description += u"La couleur liturgique est le %s." % kv['couleur']
    template.description.string += u"\n"+description

    # Inject template
    soup.channel.append(template)
    return soup.prettify()

POST_PROCESSORS = {
    "meta": office_meta_postprocess,
}

def parse_date_or_abort(date):
    try:
        year, month, day = date.split('-')
        return int(year), int(month), int(day)
    except:
        abort(400)

@app.route('/v0/office/<office>/<date>')
def get_office(office, date):
    year, month, day = parse_date_or_abort(date)
    data = get_office_for_day(office, day, month, year)

    # Don't want to cache these BUT don't want to break the app either. Should be a 404 though...
    if 'pas dans notre calendrier' in data:
        return Response(data, mimetype='application/rss+xml')

    # Do we have a secret way to enhance this ?
    if office in POST_PROCESSORS:
        data = office_meta_postprocess(data)

    # Return
    return Response(data, mimetype='application/rss+xml')

if __name__ == "__main__":
    app.run()

