# -*- coding: utf-8 -*-

import re
import copy
from bs4 import BeautifulSoup

from utils import get_office_for_day, get_office_for_day_aelf, get_asset
from utils import get_item_by_title

def postprocess(version, variant, data, day, month, year):
    # Do not enable postprocessing for versions before 20, unless beta mode
    if variant != "beta" and version < 20:
        return data

    soup = BeautifulSoup(data, 'html.parser')
    items = soup.find_all('item')

    # Scrap bénédiction from website
    complies = get_office_for_day_aelf("complies", day, month, year)
    soup_aelf = BeautifulSoup(complies, 'html.parser')
    benediction_aelf = soup_aelf.find("div", **{"class":"envoi"})

    # Early exit: we have nothing to mashup with
    if benediction_aelf is None:
        return soup.prettify()

    # Insert "Bénédiction" after "Oraison et Bénédiction" and fix it to only mention "Oraison"
    oraison_item = get_item_by_title(items, u"oraison")
    benediction_item = get_item_by_title(items, u"bénédiction")

    html_benediction = u"".join([unicode(l).strip() for l in benediction_aelf.children])
    html_oraison = benediction_item.description.string.strip()

    # This is "Oraison et bénédiction": append bénédiction
    if benediction_item == oraison_item or benediction_item is None:
        oraison_item.title.string = u"Oraison"

        benediction_item = copy.copy(items[-1])
        benediction_item.title.string = u"Bénédiction"
        benediction_item.description.string = html_benediction

        oraison_item.title.string = "Oraison"
        oraison_item.insert_after(benediction_item)

    # All done
    return soup.prettify()

