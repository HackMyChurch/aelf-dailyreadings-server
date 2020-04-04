# -*- coding: utf-8 -*-

import requests
from requests.adapters import HTTPAdapter

import yaml
from bs4 import BeautifulSoup

from collections import OrderedDict

from .exceptions import AelfHttpError
from .constants import AELF_JSON, AELF_SITE, EPITRE_CO_JSON, ASSET_BASE_PATH
from .constants import HEADERS, HTTP_TIMEOUT, OFFICE_NAME
from .postprocessor import lectures_common_cleanup
from .postprocessor import postprocess_office_lecture_title
from .postprocessor import postprocess_office_lecture_text
from .postprocessor import is_int, clean_ref, _id_to_title # FIXME

# Create a connection pool
session = requests.Session()
session.headers.update(HEADERS)
session.mount('http://',  HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

# TODO: memoization

#
# UTILS
#

def _extract_title_reference(title):
    title = title.strip(' \t\n\r')
    chunks = title.split('(', 1)
    title = chunks[0]
    if len(chunks) < 2:
        return title, ""

    reference = chunks[1].rsplit(')', 1)[0]
    return title, reference

def _do_get_request(url):
    r = session.get(url, timeout=HTTP_TIMEOUT)
    if r.status_code != 200:
        raise AelfHttpError(r.status_code)
    return r

#
# API
#

def get_office_for_day_api(office, date, region):
    '''
    Grab data from api.aelf.org and format it in a consistent way. This api is very creative in
    mixing different conventions in a single file. Output from the function is guaranteed to be
    consistent as far as the format is concerned, but is not yet post-proceced. You'll probably
    want to merge some readings befor sending.
    '''
    data = _do_get_request(AELF_JSON.format(office=office, day=date.day, month=date.month, year=date.year, region=region)).json(object_pairs_hook=OrderedDict)

    # Start to build our json format from API's format
    out = {
        u'informations': dict(data.pop('informations')),
        u'variants': [],
        u'source': 'api',
        u'office': office,
        u'date': date,
    }

    # Force 'zone' in 'informations'
    out['informations']['zone'] = region

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

        # Fix missing intermediate level (https://api.aelf.org/v1/messes/2017-07-29/romain)
        if (len(variants) > 0 and isinstance(variants[0], list)):
            variants = [{'lectures': l} for l in variants]

        for variant in variants:
            # Yes, it appends (cf Rameaux)
            if not variant['lectures']:
                continue

            # Handle variants with missing name (cf Rameaux)
            counter += 1
            if not 'nom' in variant or not variant['nom']:
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
                    patristique['titre'] = lecture
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

                if lecture.get('titre'):
                    titre = u'%s : %s' % (titre, lecture['titre'])

                texte = []

                intro       = lecture.get('intro_lue',         '').strip()
                refrain     = lecture.get('refrain_psalmique', '').strip()
                refrain_ref = lecture.get('ref_refrain',       '').strip()
                verset      = lecture.get('verset_evangile',   '').strip()
                verset_ref  = lecture.get('ref_verset',        '').strip()
                contenu     = lecture.get('contenu',           '').strip()

                if intro:
                    texte.append(u'<p><b><i>%s</i></b></p>' % intro)

                if refrain:
                    if refrain.startswith('<p>'):
                        refrain = refrain[3:-4]
                    texte.append(u'<p><font color="#CC0000">R/ %s</font></p>' % refrain)

                if verset:
                    verset = verset.strip()
                    if verset.startswith('<p>'): verset = verset[3:]
                    if verset.endswith('<p>'):   verset = verset[:-4]
                    texte.append(u'<blockquote><line><strong>Acclamation&nbsp;:</strong></br>%s<small><i>— %s</i></small></line></blockquote>' % (verset, clean_ref(verset_ref)))

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

def get_lecture_text_from_epitre(reference):
    '''
    Get the text corresponding to a reference from epitre.co API.
    Epitre.co is another website managed by @CathoGeek. It is not
    (yes) OpenSource.
    '''
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

ASSET_CACHE={}
def get_asset(path):
    # Fixme: Quick n Dirty security
    if '.' in path:
        return ""

    path = "%s/%s.yaml" % (ASSET_BASE_PATH, path)

    with open(path) as f:
        return yaml.safe_load(f)

