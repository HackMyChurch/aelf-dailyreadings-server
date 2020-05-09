# -*- coding: utf-8 -*-
'''
Grouping functions
'''

from bs4 import BeautifulSoup

def _html_to_text(text):
    soup = BeautifulSoup(text, 'html5lib')
    return soup.get_text()

def _group_before(data, title):
    '''
    Find items with title ``title`` and merge them in the ``title`` field of
    all variants of the preceding item.
    '''
    for office_variant in data['variants']:
        lectures = []
        for lecture_variants in office_variant['lectures']:
            lecture = lecture_variants[0]
            if lecture['title'].lower() == title:
                if lecture['text']:
                    for preceding_lecture_variant in lectures[-1]:
                        preceding_lecture_variant[title] = lecture['text']
                continue
            else:
                lectures.append(lecture_variants)

        office_variant['lectures'] = lectures

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
    for office_variant in data['variants']:
        lectures = []
        antienne = None
        for lecture_variants in office_variant['lectures']:
            lecture = lecture_variants[0]
            if lecture['title'].lower() == 'antienne':
                antienne = _html_to_text(lecture['text'])
                continue

            if antienne:
                for lecture in lecture_variants:
                    lecture['antienne'] = antienne
                antienne = None

            lectures.append(lecture_variants)
        office_variant['lectures'] = lectures

def group_oraison_benediction(data):
    '''
    Find 'benediction' items. If the preceding item is "oraison", make it an
    oraison and benediction item.
    '''
    for office_variant in data['variants']:
        lectures = []
        for lecture_variants in office_variant['lectures']:
            lecture = lecture_variants[0]
            if 'benediction' in lecture['key'] and lectures[-1][0]['title'].lower() == 'oraison':
                lectures[-1][0]['title'] = "Oraison et bénédiction"
                lectures[-1][0]['text'] += lecture['text']
                continue
            lectures.append(lecture_variants)

        office_variant['lectures'] = lectures

def group_lecture_variants(data):
    '''
    Merge lectures with identical "key.orig" and offer them as lecture variants.
    '''
    # First pass: merge
    for office_variant in data['variants']:
        lectures = []
        prev_key = None
        for lecture_variants in office_variant['lectures']:
            key = lecture_variants[0].get('key.orig')
            if key and key == prev_key:
                lectures[-1].extend(lecture_variants)
                continue
            prev_key = key
            lectures.append(lecture_variants)
        office_variant['lectures'] = lectures

    # Second pass: generate variant titles
    for office_variant in data['variants']:
        for lecture_variants in office_variant['lectures']:
            if len(lecture_variants) < 2:
                continue
            elif len(lecture_variants) == 2 and 'LECTURE BREVE' in lecture_variants[0]['text']:
                lecture_variants[0]['variant_title'] = "Lecture longue"
                lecture_variants[1]['variant_title'] = "Lecture brève"
            elif len(lecture_variants) == 2:
                lecture_0 = lecture_variants[0]
                lecture_1 = lecture_variants[1]
                book_chapter_0 = lecture_0['reference'].split(',')[0]
                book_chapter_1 = lecture_1['reference'].split(',')[0]

                is_psalm                   = (lecture_0['short_title'].strip().lower() == 'psaume')
                have_distinct_short_titles = (lecture_0['short_title'] != lecture_1['short_title'])
                have_distinct_long_titles  = (lecture_0['long_title'] != lecture_1['long_title'])
                have_distinct_chapter      = (book_chapter_0 != book_chapter_1)

                if have_distinct_short_titles:
                    if have_distinct_chapter:
                        lecture_0['variant_title'] = f"{lecture_0['short_title']} ({book_chapter_0})"
                        lecture_1['variant_title'] = f"{lecture_1['short_title']} ({book_chapter_1})"
                    else:
                        lecture_0['variant_title'] = f"{lecture_0['short_title']}"
                        lecture_1['variant_title'] = f"{lecture_1['short_title']}"
                elif have_distinct_long_titles:
                    if have_distinct_chapter:
                        lecture_0['variant_title'] = f"{lecture_0['long_title']} ({book_chapter_0})"
                        lecture_1['variant_title'] = f"{lecture_1['long_title']} ({book_chapter_1})"
                    else:
                        lecture_0['variant_title'] = f"{lecture_0['long_title']}"
                        lecture_1['variant_title'] = f"{lecture_1['long_title']}"
                elif is_psalm and have_distinct_chapter:
                    lecture_0['variant_title'] = f"{lecture_0['short_title']} {book_chapter_0.split(' ')[1]}"
                    lecture_1['variant_title'] = f"{lecture_1['short_title']} {book_chapter_1.split(' ')[1]}"
                elif have_distinct_chapter:
                    lecture_0['variant_title'] = f"{lecture_0['short_title']} ({book_chapter_0})"
                    lecture_1['variant_title'] = f"{lecture_1['short_title']} ({book_chapter_1})"
                else:
                    lecture_0['variant_title'] = f"{lecture_0['short_title']} ({lecture_0['reference']})"
                    lecture_1['variant_title'] = f"{lecture_1['short_title']} ({lecture_1['reference']})"
            else:
                for lecture in lecture_variants:
                    lecture['variant_title'] = f"{lecture['short_title']} ({lecture['reference']})"

def group_related_items(version, mode, data):
    '''
    Group related items so that verse, antienne, repons and similar items are
    attached to their main psalm, cantique, pericope, lecture, ...
    '''
    group_antienne(data)
    group_repons(data)
    group_verset(data)
    group_oraison_benediction(data)

    if version >= 68:
        group_lecture_variants(data)

    return data

