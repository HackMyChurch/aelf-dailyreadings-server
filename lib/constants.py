# -*- coding: utf-8 -*-

import os

# Base URL / Paths
AELF_JSON="https://api.aelf.org/v1/{office}/{year:04d}-{month:02d}-{day:02d}"
AELF_SITE="http://www.aelf.org/{year:04d}-{month:02d}-{day:02d}/romain/{office}"
EPITRE_CO_JSON="http://epitre.co/api/1.0/ref/fr-lit/{reference}"
ASSET_BASE_PATH=os.path.join(os.path.abspath(os.path.dirname(__file__)), "../assets")

# HTTP client configuration
HEADERS={'User-Agent': 'AELF - Lectures du jour - API - cathogeek@epitre.co'}
HTTP_TIMEOUT = 10 # seconds

# French constants
DETERMINANTS = [
        'd', 'l', 'l\'', 'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'd\'', 'au', u'à',
        'ma', 'ta', 'sa', 'mon', 'ton', 'son', 'notre', 'votre', 'leur,'
        'mais', 'ou', 'et', 'donc', 'sur', 'sans',
        'ce', 'ces', 'cela', 'cette', 'celui', 'celle', 'celles', 'ceux', u'ça',
        'pour', 'afin', 'contre', 'avec', 'en',

        # Most common common names
        'saint', 'sainte', 'anniversaire', 'ordination', 'sermon', 'homelie', u'homélie',
        'grand', 'grande',
];

# Simple translation tables
OFFICE_NAME = {
    "messes": "messe",
}

ID_TO_TITLE = {
    'benediction': u'Bénédiction',
}

