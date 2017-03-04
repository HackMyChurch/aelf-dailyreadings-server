# -*- coding: utf-8 -*-

import re
import copy

from utils import get_asset
from utils import get_item_by_title
from utils import get_lecture_by_type, insert_lecture_before, insert_lecture_after

def postprocess(version, variant, data, date):
    # Do not enable postprocessing for versions before 20, unless beta mode
    if variant != "beta" and version < 20:
        return data

    # Attempt to load oraison item. If we can't, gracefully degrade
    oraison_item = get_lecture_by_type(data, u"oraison")
    if oraison_item is None:
        return data

    # Fix Notre Père
    notre_pere = get_asset('prayers/notre-pere')
    notre_pere_item = get_lecture_by_type(data, u"notre_pere")
    notre_pere_lecture = {
        'title':     notre_pere['title'],
        'text':      notre_pere['body'],
        'reference': '',
        'key':       'te_deum',
    }

    if notre_pere_item:
        notre_pere_item.lecture.update(notre_pere_lecture)
    else:
        insert_lecture_before(data, notre_pere_lecture, oraison_item)

    # Append Benediction
    benediction = get_asset('prayers/laudes-benediction')
    benediction_lecture = {
        'title':     benediction['title'],
        'text':      benediction['body'],
        'reference': '',
        'key':       'benediction',
    }
    insert_lecture_after(data, benediction_lecture, oraison_item)

    # All done
    return data

