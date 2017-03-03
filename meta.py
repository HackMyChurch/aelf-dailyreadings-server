# -*- coding: utf-8 -*-

import re
from bs4 import BeautifulSoup
from utils import json_to_rss

def postprocess(version, variant, data, day, month, year):
    informations = data['informations']
    out = {
        'informations': informations,
        'variants': [
            {
                'name': 'Informations',
                'lectures': [
                    {
                        'title':     'Jour liturgique',
                        'text':      informations['text'],
                        'reference': '',
                        'key':       'informations',
                    }
                ]
            }
        ]
    }

    return json_to_rss(out)

