# -*- coding: utf-8 -*-

import re

from .constants import ID_TO_TITLE
from .constants import DETERMINANTS
from .office import get_lecture_by_type, insert_lecture_before, insert_lecture_after

#
# Utils
#

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

PSALM_MATCH=re.compile('^[0-9]+(-[IV0-9]+)?$')
def _is_psalm_ref(data):
    return re.match(PSALM_MATCH, data.replace(' ', ''))

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
    if _is_letter(chunks[0]) or (len(chunks) > 1 and _is_letter(chunks[1])):
        return ref

    return 'Ps %s' % ref

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

#
# API
#

# TODO: handle '
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

# FIXME: this function is only used by the libs and does not follow te same convention as the otthers
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
            print lecture['key']
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
                elif lecture['title'] == "Psaume" and _is_psalm_ref(raw_ref):
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
            print "-->", lecture['title']
            lecture['title'] = lecture['title'].replace(u'\xa0', u' ');

    # PASS 2: merge meargable items

    return data

# TODO: move me to a common postprocessor file
def postprocess_office_careme(version, mode, data):
    '''
    Remove "Alleluia" from introduction slide if the periode is careme
    '''
    if data['informations'].get('temps_liturgique', '') != 'careme':
        return

    introduction_item = get_lecture_by_type(data, u"introduction")
    introduction_item.lecture['text'] = introduction_item.lecture['text'].replace(u'(Alléluia.)', '')

def postprocess_office_keys(version, mode, data):
    '''
    Posprocess office keys so that they are as compatible as possible
    with AELF's website. Special care needs to be taken. Skip this
    funtion when the source is not the API (ie: comming from the website)
    '''
    if data['source'] != 'api':
        return data

    for variant in data['variants']:
        for lecture in variant['lectures']:
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

def postprocess_office_common(version, mode, data):
    '''
    Run all office-specific postprocessing
    '''
    postprocess_office_careme(version, mode, data)
    postprocess_office_keys(version, mode, data)
    return data

