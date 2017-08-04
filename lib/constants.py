# -*- coding: utf-8 -*-

import os

CURRENT_VERSION = 39

# Base URL / Paths
AELF_JSON="https://api.aelf.org/v1/{office}/{year:04d}-{month:02d}-{day:02d}/{region}"
AELF_SITE="http://www.aelf.org/{year:04d}-{month:02d}-{day:02d}/{region}/{office}"
EPITRE_CO_JSON="http://epitre.co/api/1.0/ref/fr-lit/{reference}"
ASSET_BASE_PATH=os.path.join(os.path.abspath(os.path.dirname(__file__)), "../assets")
DEFAULT_REGION="romain"

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

# HTML
HTML_BLOCK_ELEMENTS = [
        "body",
        "section", "nav",
        "header", "footer",
        "table", "thread", "tbody", "td", "tr", "th",
        "div", "p", "blockquote",
]

# Simple translation tables
OFFICE_NAME = {
    "messes": "messe",
}

ID_TO_TITLE = {
    'benediction': u'Bénédiction',
}

# Region specific settings
REGION_NOTRE_PERE_NEW = ['belgique', 'afrique']

# Internal Monitoring
# The application syncs up to 30 days in the future. This gives 2 week to fix errors
STATUS_DAYS_TO_MONITOR = int(os.environ.get('AELF_STATUS_DAYS_TO_MONITOR', 45))

# 404 error become fatal 2 weeks ahead
STATUS_DAYS_404_FATAL = 15

STATUS_PROBE_INTERVAL = 3600 * 24
STATUS_PROBE_INTERVAL_ERROR = 60 * 15

