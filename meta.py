# -*- coding: utf-8 -*-

import re

def postprocess(version, mode, data):
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

