# -*- coding: utf-8 -*-

import re
from bs4 import BeautifulSoup

from utils import get_office_for_day, get_pronoun_for_letter

# TODO: memoization
def postprocess(data):
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
    has_fete = False
    if 'jour' in kv:
        description += kv['jour']
    if 'fete' in kv and ('jour' not in kv or kv['jour'] not in kv['fete']):
        fete = re.sub(r'(\w)(S\.|Ste) ', r'\1, \2 ', kv['fete']) # Fix word splitting when multiple Saints
        fete = fete.replace("S.", "Saint").replace("Ste", "Sainte")
        if description:
            if ' ' not in fete:
                pronoun = get_pronoun_for_letter(kv['fete'][0].lower())
                description += " de %s " % pronoun
            elif u'férie' in fete:
                description += u" "
            else:
                description += u". Nous fêtons "
                if kv['fete'][0] != 'S':
                    pronoun = get_pronoun_for_letter(kv['fete'][0].lower())
                    description += "%s " % pronoun

        has_fete = True
        description += fete
    if 'semaine' in kv:
        if has_fete:
            description += u'. '
        elif description:
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

