# -*- coding: utf-8 -*-
'''
Grouping functions
'''

def _group_before(data, title):
    '''
    Find items with title ``title`` and merge them in the ``title`` fiels of
    them preceding item.
    '''
    for variant in data['variants']:
        lectures = []
        for lecture in variant['lectures']:
            if lecture['title'].lower() == title:
                if lecture['text']:
                    lectures[-1][title] = lecture['text']
                continue
            else:
                lectures.append(lecture)

        variant['lectures'] = lectures

def group_repons(data):
    '''
    Group 'repons' field in the preceding slide.
    '''
    return _group_before(data, 'repons')

def group_verset(data):
    '''
    Group 'verset' field in the preceding slide.
    '''
    return _group_before(data, 'verset')

def group_antienne(data):
    '''
    Find 'antienne' items and merge them in the 'antienne' field of the
    following slide.
    '''
    for variant in data['variants']:
        lectures = []
        antienne = None
        for lecture in variant['lectures']:
            if lecture['title'].lower() == 'antienne':
                antienne = lecture['text']
                continue

            if antienne:
                lecture['antienne'] = antienne
                antienne = None

            lectures.append(lecture)
        variant['lectures'] = lectures

def group_oraison_benediction(data):
    '''
    Find 'benediction' items. If the precdeing item is "oraison", make it an
    oraison and benediction item.
    '''
    for variant in data['variants']:
        lectures = []
        for lecture in variant['lectures']:
            if 'benediction' in lecture['key'] and lectures[-1]['title'].lower() == 'oraison':
                lectures[-1]['title'] = u"Oraison et bénédiction"
                lectures[-1]['text'] += lecture['text']
                continue
            lectures.append(lecture)

        variant['lectures'] = lectures

def group_related_items(data):
    '''
    Group related items so that verse, antienne, repons and similar items are
    attached to their main psalm, cantique, pericope, lecture, ...
    '''
    group_antienne(data)
    group_repons(data)
    group_verset(data)
    group_oraison_benediction(data)
    return data

