# -*- coding: utf-8 -*-

import re
import datetime

from utils import get_asset, get_office_for_day_aelf_json, get_lecture_text_from_epitre
from utils import get_lectures_by_type, get_lecture_by_type, insert_lecture_before
from lib.postprocessor import postprocess_office_html_lecture
from lib.postprocessor import postprocess_office_lecture_text

def postprocess(version, mode, data):
    # Do not enable postprocessing for versions before 20, unless beta mode
    if mode != "beta" and version < 20:
        return data

    date = data['date']
    te_deum_item = get_lecture_by_type(data, u"office_te_deum")
    lecture_item = get_lecture_by_type(data, u"office_lecture")
    repons_item  = get_lecture_by_type(data, u"office_repons_lecture")
    oraison_item = get_lecture_by_type(data, u"office_oraison")

    # Fix missing "Lecture"
    if lecture_item is None and repons_item is not None:
        # Grab lectures from the website, still json format
        data_aelf = get_office_for_day_aelf_json("lectures", date, data['informations']['zone'])

        # Attempt to get the lecture
        lecture_items = get_lectures_by_type(data_aelf, u"office_lecture")
        lecture_items = [l for l in lecture_items if l.lecture['title'].lower() not in ['verset', 'repons']]
        lecture_item = lecture_items[0] if lecture_items else None

        # If we've got a lecture item, insert it before the repons
        insert_lecture_before(data, lecture_item.lecture, repons_item)

    # Fix empty "Lecture"..., try to load it from epitre.co
    # FIXME: embark these data and NEVER load from AELF, too much broken
    if lecture_item and not lecture_item.lecture['text']:
        try:
            lecture_item.lecture['text'] = get_lecture_text_from_epitre(lecture_item.lecture['reference'])
            lecture_item.lecture['text'] = postprocess_office_lecture_text(version, mode, lecture_item.lecture['text'])
        except:
            # This is best effort. We don't want the fallback path to bring the whole stuff down !
            pass

    # Fix missing "Te Deum" on Sunday
    if te_deum_item is None and oraison_item and date.isoweekday() == 7:
        te_deum = get_asset('prayers/te-deum')
        te_deum_lecture = {
            'title':     te_deum['title'],
            'text':      te_deum['body'],
            'reference': '',
            'key':       'te_deum',
        }
        postprocess_office_html_lecture(version, mode, te_deum_lecture)
        insert_lecture_before(data, te_deum_lecture, oraison_item)

    # Fix oraison slide title: there is no benediction
    if oraison_item is not None:
        oraison_item.lecture['title'] = "Oraison"

    # All done
    return data

