# -*- coding: utf-8 -*-

import re
from utils import json_to_rss

def postprocess(version, variant, data):
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

    return out

