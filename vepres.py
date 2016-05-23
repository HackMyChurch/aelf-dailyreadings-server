# -*- coding: utf-8 -*-

import re
import copy
from bs4 import BeautifulSoup

from utils import get_office_for_day, get_asset
from utils import get_item_by_title

def postprocess(data, day, month, year):
    soup = BeautifulSoup(data, 'xml')
    items = soup.find_all('item')

    # Missing "Notre Père" ?
    if get_item_by_title(items, u"Notre Père") is None:

        # Get item where to insert
        oraison = get_item_by_title(items, u"oraison")
        if oraison is not None:
            notre_pere = get_asset('prayers/notre-pere')
            notre_pere_item = copy.copy(items[-1])
            notre_pere_item.title.string = notre_pere['title']
            notre_pere_item.description.string = notre_pere['body']

            oraison.insert_before(notre_pere_item)

    # All done
    return soup.prettify()

