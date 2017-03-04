# -*- coding: utf-8 -*-

import re
from utils import json_to_rss, fix_case, AELF_SITE

def postprocess_keys(version, mode, data, day, month, year):
    '''
    Rewrite keys to match AELF's website convention
    '''
    messe_counter = 0
    for variant in data['variants']:
        messe_counter += 1
        lecture_counter = 0
        for lecture in variant['lectures']:
            lecture_counter += 1
            lecture['key.orig'] = lecture['key']
            lecture['key'] = "messe%s_lecture%s" % (messe_counter, lecture_counter)

def postprocess_links(version, mode, data, day, month, year):
    '''
    Generate a link page on compatible versions
    '''
    # No support for links in the app, sorry
    if version < 29:
        return data

    # Not applicable if there is a single mass
    if len(data['variants']) < 2:
        return data

    # PASS 1: detect + fix known to be broken cases
    if data['variants'][0]['lectures'][0]['key.orig'] == "entree_messianique":
        data['variants'][ 0]['name'] = u"Entrée messianique"
        data['variants'][-1]['name'] = u"Messe du jour"

    # Fix may friend the all-caps...
    for variant in data['variants']:
        variant['name'] = fix_case(variant['name'])

    # PASS 2: collect the data
    variant_data = [];
    for variant in data['variants']:
        variant_data.append({
            'name': variant['name'],
            'key':  variant['lectures'][0]['key'],
        })

    # GENERATE the title slide
    links = ""
    base_link = AELF_SITE.format(year=year, month=month, day=day, office='messe')
    for variant_counter, variant in enumerate(variant_data):
        links += '<a href="%s#%s" class="variant-%s">%s</a>' % (base_link, variant['key'], variant_counter, variant['name'])

    # PASS 3: Insert the title slide before each variant
    for variant_counter, variant in enumerate(data['variants']):
        text = links.replace('class="variant-%s"' % variant_counter, 'class="variant-%s active"' % variant_counter)
        variant['lectures'].insert(0, {
            'title':     'Messes',
            'text':      '<div class="app-office-navigation">%s</div>' % text,
            'reference': '',
            'key':       'navigation',
        })

def postprocess(version, mode, data, day, month, year):
    postprocess_keys(version, mode, data, day, month, year)
    postprocess_links(version, mode, data, day, month, year)

    return json_to_rss(data)

