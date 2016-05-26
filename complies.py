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

    soup = BeautifulSoup(data, 'xml')
    items = soup.find_all('item')

    # Scrap bénédiction from website
    complies = get_office_for_day_aelf("complies", day, month, year)
    soup_aelf = BeautifulSoup(complies, 'xml')
    benediction_aelf = soup_aelf.find("div", **{"class":"envoi"})

    # Early exit: we have nothing to mashup with
    if benediction_aelf is None:
        return soup.prettify()

    # Insert "Bénédiction" after "Oraison et Bénédiction" and fix it to only mention "Oraison"
    oraison = get_item_by_title(items, u"oraison")
    benediction = get_item_by_title(items, u"bénédiction")
    html_benediction = u"".join([unicode(l) for l in benediction_aelf.children])

    # This is "Oraison et bénédiction" --> split + insert new benediction on dedicated slide
    # TODO: future versions, keep it "oraison et bénédiction"
    if benediction == oraison or oraison is None:
        benediction = copy.copy(oraison)
        oraison.title.string = u"Oraison"
        benediction.title.string = u"Bénédiction"
        benediction.description.string = html_benediction
        oraison.insert_after(benediction)

    # All done
    return soup.prettify()

