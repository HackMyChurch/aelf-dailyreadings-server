# -*- coding: utf-8 -*-

import re
import copy
from bs4 import BeautifulSoup

from utils import get_office_for_day, get_asset
from utils import get_item_by_title

def postprocess(version, variant, data, day, month, year):
    # Do not enable postprocessing for versions before 20, unless beta mode
    if variant != "beta" and version < 20:
        return data

    soup = BeautifulSoup(data, 'xml')
    items = soup.find_all('item')

    te_deum_item = get_item_by_title(items, u"te deum")
    oraison_item = get_item_by_title(items, u"oraison")
    envoi_item = get_item_by_title(items, u"envoi")

    # Fix empty "Te Deum"
    if te_deum_item is not None and oraison_item:
        te_deum = get_asset('prayers/te-deum')
        te_deum_item.description.string = te_deum['body']

        # Fix: te deum not at the right location
        te_deum_item.extract()
        oraison_item.insert_before(te_deum_item)

    # Fix oraison slide title: there is no benediction
    if oraison_item is not None:
        oraison_item.title.string = "Oraison"

    # Fix missing envoi part
    if envoi_item is not None:
        envoi = get_asset('prayers/lectures-envoi')

        if not u'<p' in envoi_item.description.string:
            envoi_item.description.string = u"<p>%s</p>" % envoi_item.description.string

        envoi_item.description.string += "<blockquote>%s</blockquote>" % envoi['body']

    # All done
    return soup.prettify()

