# -*- coding: utf-8 -*-

import re

def postprocess(version, mode, data):
    data['variants'] = [
        {
            'name': 'Informations',
            'lectures': [
                [{
                    'title':     'Jour liturgique',
                    'text':      data['informations']['text'],
                    'reference': '',
                    'key':       'informations',
                }]
            ]
        }
    ]

    return data

