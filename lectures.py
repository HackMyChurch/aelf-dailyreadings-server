# -*- coding: utf-8 -*-

import re
import datetime

from utils import get_asset
from utils import json_to_rss, get_lecture_by_type, insert_lecture_before

def postprocess(version, mode, data, day, month, year):
    # Do not enable postprocessing for versions before 20, unless beta mode
    if mode != "beta" and version < 20:
        return data

    te_deum_item = get_lecture_by_type(data, u"te_deum")
    lecture_item = get_lecture_by_type(data, u"lecture")
    oraison_item = get_lecture_by_type(data, u"oraison")

    # Fix missing "Lecture"
    if lecture_item is None:
        pass

    # Fix missing "Te Deum" on Sunday
    if te_deum_item is None and oraison_item and datetime.date(year, month, day).isoweekday() == 7:
        te_deum = get_asset('prayers/te-deum')
        te_deum_lecture = {
            'title':     te_deum['title'],
            'text':      te_deum['body'],
            'reference': '',
            'key':       'te_deum',
        }
        insert_lecture_before(data, te_deum_lecture, oraison_item)

    # Fix oraison slide title: there is no benediction
    if oraison_item is not None:
        oraison_item.lecture['title'] = "Oraison"

    # All done
    return json_to_rss(data)

