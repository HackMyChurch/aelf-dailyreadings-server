# -*- coding: utf-8 -*-

import re
import datetime

from utils import get_asset, get_lecture_text_from_epitre
from utils import get_lectures_by_type, get_lecture_by_type, insert_lecture_before
from lib.postprocessor import postprocess_office_html_lecture
from lib.postprocessor import postprocess_office_lecture_text

def postprocess_easter(version, mode, data):
    text = u"""<p>
    Le jour de Pâques est un jour spécial. C'est le jour de la résurrection
    du Christ. Il n'y a pas d'office des lectures ce jour là.
    </p>"""

    data['source'] = "api"
    data['variants'] = [
        {
            u'name': u'Dimanche de Pâques',
            u'lectures': [
                {
                    u'title':     u'Lectures: Le saviez-vous ?',
                    u'text':      text,
                    u'reference': '',
                    u'key':       '',
                }
            ]
        }
    ]
    return data

def postprocess(version, mode, data):
    if data['informations'].get('temps_liturgique', '') == "triduum" and data['informations'].get('jour', '') == "dimanche":
        return postprocess_easter(version, mode, data)

    # Do not enable postprocessing for versions before 20, unless beta mode
    if mode != "beta" and version < 20:
        return data

    date = data['date']
    te_deum_item = get_lecture_by_type(data, u"office_te_deum")
    lecture_item = get_lecture_by_type(data, u"office_lecture")
    repons_item  = get_lecture_by_type(data, u"office_repons_lecture")
    oraison_item = get_lecture_by_type(data, u"office_oraison")

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

