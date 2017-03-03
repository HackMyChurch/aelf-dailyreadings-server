# -*- coding: utf-8 -*-

import re
import copy
from bs4 import BeautifulSoup

from utils import get_asset
from utils import get_item_by_title

def postprocess(version, variant, data, day, month, year):
    # Do not enable postprocessing for versions before 20, unless beta mode
    if variant != "beta" and version < 20:
        return data

    soup = BeautifulSoup(data, 'html.parser')
    items = soup.find_all('item')

    oraison_item = get_item_by_title(items, u"oraison")
    if oraison_item is None:
        # Fallback
        return data

    # "Notre Père"
    notre_pere_item = get_item_by_title(items, u"Notre Père")
    if notre_pere_item is None:
        notre_pere_item = get_item_by_title(items, u"Notre pere")

    if notre_pere_item is None:
        notre_pere_item = copy.copy(items[-1])

    notre_pere = get_asset('prayers/notre-pere')
    notre_pere_item.title.string = notre_pere['title']
    notre_pere_item.description.string = notre_pere['body']

    oraison_item.insert_before(notre_pere_item)

    # Append dedicated "Bénédiction" slide
    benediction = get_asset('prayers/vepres-benediction')
    benediction_item = copy.copy(items[-1])
    benediction_item.title.string = benediction['title']
    benediction_item.description.string = benediction['body']

    oraison_item.title.string = "Oraison"
    oraison_item.insert_after(benediction_item)

    # All done
    return soup.prettify()

