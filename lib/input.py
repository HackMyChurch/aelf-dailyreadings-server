import requests
from requests.adapters import HTTPAdapter

import yaml

from collections import OrderedDict

from .exceptions import AelfHttpError
from .constants import AELF_JSON, ASSET_BASE_PATH
from .constants import HEADERS, HTTP_TIMEOUT, OFFICE_NAME
from .postprocessor import lectures_common_cleanup
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

def _do_get_request(url):
    r = session.get(url, timeout=HTTP_TIMEOUT)
    if r.status_code != 200:
        raise AelfHttpError(r.status_code)
    return r

#
# API
#

class NonNoneOrderedDict(OrderedDict):
    def __init__(self, pairs):
        super().__init__((p for p in pairs if p[1] is not None))

def get_office_for_day_api(office, date, region):
    '''
    Grab data from api.aelf.org and format it in a consistent way. This api is very creative in
    mixing different conventions in a single file. Output from the function is guaranteed to be
    consistent as far as the format is concerned, but is not yet post-processed. You'll probably
    want to merge some readings before sending.
    '''
    data = _do_get_request(AELF_JSON.format(office=office, day=date.day, month=date.month,
                           year=date.year, region=region)).json(object_pairs_hook=NonNoneOrderedDict)

    # Start to build our json format from API's format
    out = {
        'informations': dict(data.pop('informations')),
        'variants': [],
        'source': 'api',
        'office': office,
        'date': date,
    }

    # Force 'zone' in 'informations'
    out['informations']['zone'] = region

    # 'information' office has no reading
    # FIXME: in the future, we'll get informations through "mass" only, and this case should move
    #        compat API should use it and postprocess informations for each office
    if not data:
        return lectures_common_cleanup(out)

    # PASS 1: Normalize data to a list of office variants. Each variant is a list of offices with a type
    # we use lists to 1/ preserve order 2/ allow for duplicates like "short version"
    name, variants = list(data.items()).pop()
    if isinstance(variants, list):
        # Mass: multiple variants, lectures list inside, possible collision on types
        counter = 0; # We'll need it to generate variants name in case it's missing
        cleaned = []

        # Fix missing intermediate level (https://api.aelf.org/v1/messes/2017-07-29/romain)
        if (len(variants) > 0 and isinstance(variants[0], list)):
            variants = [{'lectures': l} for l in variants]

        for variant in variants:
            # (eg Rameaux)
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
            'titre': '',
            'texte': '',
        }

        for name, lecture in variants.items():
            # 'lecture' may not be a dict yet...
            if isinstance(lecture, str):
                # Re-assemble patristique text...
                if name == 'titre_patristique':
                    patristique['titre'] = lecture
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
                        titre = f"1ère {titre}"
                    else:
                        titre = f"{number}ème {titre}"

                if lecture.get('titre'):
                    titre = '%s : %s' % (titre, lecture['titre'])

                texte = []

                intro       = lecture.get('intro_lue',         '').strip()
                refrain     = lecture.get('refrain_psalmique', '').strip()
                verset      = lecture.get('verset_evangile',   '').strip()
                verset_ref  = lecture.get('ref_verset',        '').strip()
                contenu     = lecture.get('contenu',           '').strip()

                if intro:
                    texte.append(f'<p><b><i>{intro}</i></b></p>')

                if verset:
                    verset = verset.strip()
                    if verset.startswith('<p>'): verset = verset[3:]
                    if verset.endswith('</p>'):  verset = verset[:-4]
                    texte.append('<blockquote><span class="line"><strong>Acclamation&nbsp;:</strong></br>%s<small><i>— %s</i></small></span></blockquote>' % (verset, clean_ref(verset_ref)))

                texte.append('<div class="content">')

                if refrain:
                    if refrain.startswith('<p>'):
                        refrain = refrain[3:-4]
                    texte.append(f'<p><font color="#CC0000">R/ {refrain}</font></p>')

                if contenu:
                    texte.append(contenu)

                texte.append('</div>')

                lecture_cleaned = {
                    'title':     titre,
                    'reference': lecture['ref'],
                    'intro':     intro,
                    'text':      ''.join(texte),
                }
            else:
                # Gather the cleaned fields as a *list* of lecture variants.
                # (AELF API has a single lecture variant, but we'll add more)
                lecture_cleaned = {
                    'title':     lecture.get('titre',     ''),
                    'reference': lecture.get('reference', ''),
                    'intro':     lecture.get('intro',     ''),
                    'text':      lecture.get('texte',     ''),
                }

            # Common fields
            lecture_cleaned['key'] = name
            for aelf_field_name, app_field_name in [('auteur', 'author'), ('editeur', 'editor')]:
                if value := lecture.get(aelf_field_name):
                    lecture_cleaned[app_field_name] = value

            cleaned = [lecture_cleaned]

            out_variant['lectures'].append(cleaned)

    return lectures_common_cleanup(out)


ASSET_CACHE={}
def get_asset(path):
    # Fixme: Quick n Dirty security
    if '.' in path:
        return ""

    path = "%s/%s.yaml" % (ASSET_BASE_PATH, path)

    with open(path) as f:
        return yaml.safe_load(f)

