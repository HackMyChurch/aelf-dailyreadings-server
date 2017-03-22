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
DETERMINANTS = ['l\'', 'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'd\'', 'au', u'à'];

# Simple translation tables
OFFICE_NAME = {
    "messes": "messe",
}

ID_TO_TITLE = {
    'benediction': u'Bénédiction',
}

