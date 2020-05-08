# -*- coding: utf-8 -*-

import re
import copy

from utils import get_asset
from utils import get_lecture_variants_by_type, insert_lecture_variants_before, insert_lecture_variants_after
from lib.postprocessor import postprocess_office_html_lecture
from lib.constants import REGION_NOTRE_PERE_NEW

def insert_inviting_pslams_variants(version, mode, data):
    '''
    There are 4 possible inviting psalms. Only the most commonly used in
    returned by AELF's API. Insert the 4 other variants.
    '''
    psalm_variants_item = get_lecture_variants_by_type(data, "office_psaume_invitatoire")
    if psalm_variants_item is None:
        return

    for psalm_id in ['66', '99', '23']:
        psalm = get_asset(f'psalms/psalm-{psalm_id}')
        psalm_item = {
            'title':     psalm_variants_item.lectureVariants[0]['title'],
            'text':      psalm['body'],
            'reference': psalm['reference'],
            'key':       psalm_variants_item.lectureVariants[0]['key'],
        }
        postprocess_office_html_lecture(version, mode, psalm_item)
        psalm_variants_item.lectureVariants.append(psalm_item)

def postprocess(version, mode, data):
    '''
    Common postprocessing code for laudes and vepres. These are very similar offices
    '''
    # Do not enable postprocessing for versions before 20, unless beta mode
    if mode != "beta" and version < 20:
        return data

    # Insert alternative inviting psalm
    insert_inviting_pslams_variants(version, mode, data)

    # Attempt to load oraison item. If we can't, gracefully degrade
    oraison_item = get_lecture_variants_by_type(data, "office_oraison")
    if oraison_item is None:
        return data

    # Fix Notre Père
    notre_pere = get_asset('prayers/notre-pere')
    notre_pere_item = get_lecture_variants_by_type(data, "office_notre_pere")
    notre_pere_lecture = {
        'title':     notre_pere['title'],
        'text':      notre_pere['body'],
        'reference': '',
        'key':       'office_notre_pere',
    }
    postprocess_office_html_lecture(version, mode, notre_pere_lecture)

    if notre_pere_item:
        notre_pere_item.lectureVariants[0].update(notre_pere_lecture)
    else:
        insert_lecture_variants_before(data, [notre_pere_lecture], oraison_item)

    # Append Benediction
    benediction = get_asset('prayers/%s-benediction' % data['office'])
    benediction_lecture = {
        'title':     benediction['title'],
        'text':      benediction['body'],
        'reference': '',
        'key':       'benediction',
    }
    postprocess_office_html_lecture(version, mode, benediction_lecture)
    insert_lecture_variants_after(data, [benediction_lecture], oraison_item)

    # All done
    return data

