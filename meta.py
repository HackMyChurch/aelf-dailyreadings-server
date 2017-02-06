# -*- coding: utf-8 -*-

import re
from bs4 import BeautifulSoup

from utils import get_office_for_day, get_pronoun_for_sentence

def _filter_fete(fete):
    '''fete can be proceesed from 2 places. Share common filtering code'''
    fete = re.sub(r'(\w)(S\.|St|Ste) ', r'\1, \2 ', fete) # Fix word splitting when multiple Saints
    return fete.replace("S. ", "Saint ")\
               .replace("St ", "Saint ")\
               .replace("Ste ", "Sainte ")

# TODO: memoization
def postprocess(version, variant, data, day, month, year):
    # Do not enable postprocessing for versions before 20, unless beta mode
    if variant != "beta" and version < 20:
        return data

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
    fete_done = False
    fete_skip = False

    # Never print fete if this is the semaine
    if kv.get('fete', '').split(' ')[0] == kv.get('semaine', '').split(' ')[0]:
        fete_skip = True

    if 'jour' in kv:
        description += kv['jour']
        if not fete_skip and 'fete' in kv:
            fete = _filter_fete(kv['fete'])

            # Single word (paque, ascension, noel, ...)
            if ' ' not in fete:
                pronoun = get_pronoun_for_sentence(fete)
                description += u" de %s%s" % (pronoun, fete)
                fete_done = True
            # De la férie
            elif u'férie' in fete:
                description += u" " + fete
                fete_done = True
    if 'semaine' in kv:
        if description:
            description += u', '
        description += kv['semaine']
    if 'annee' in kv:
        if description:
            if fete_done:
                description += u", année %s" % kv['annee']
            else:
                description += u" de l'année %s" % kv['annee']
        else:
            description += u"Année %s" % kv['annee']

    if description:
        description += "."

    if not fete_skip and not fete_done and 'fete' in kv and ('jour' not in kv or kv['jour'] not in kv['fete']):
        fete = _filter_fete(kv['fete'])
        verbe = u"fêtons" if u'saint' in fete.lower() else u"célèbrons"

        # Single word (paque, ascension, noel, ...)
        if ' ' not in fete:
            description += u" Nous %s %s." % (verbe, fete)
        # Standard fete
        if u'férie' not in fete:
            pronoun = get_pronoun_for_sentence(fete)
            description += u' Nous %s %s%s.' % (verbe, pronoun, fete)

    if 'couleur' in kv:
        description += u" La couleur liturgique est le %s." % kv['couleur']

    # Final cleanup: 1er, 1ère, 2ème, 2nd, ... --> exposant
    description = re.sub(ur'([0-9])(er|nd|ère|ème) ', r'\1<sup>\2</sup> ', description)
    description = description[:1].upper() + description[1:]

    # Inject template
    template.description.string += u"\n"+description
    soup.channel.append(template)
    return soup.prettify()

