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

    # Fix empty "Te Deum"
    te_deum_item = get_item_by_title(items, u"te deum")
    oraison_item = get_item_by_title(items, u"oraison")

    if te_deum_item is not None:
        te_deum = get_asset('prayers/te-deum')
        te_deum_item.description.string = te_deum['body']

        # Fix: te deum not at the right location
        te_deum_item.extract()
        oraison_item.insert_before(te_deum_item)

    # Fix oraison slide title: there is no benediction
    oraison_item.title.string = "Oraison"

    # All done
    return soup.prettify()

