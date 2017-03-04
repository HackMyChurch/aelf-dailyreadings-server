#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Response, abort, request
app = Flask(__name__)

import os
import time
import json
import meta
import messes
import laudes_vepres
import lectures
import datetime
from utils import get_office_for_day_api, get_office_for_day_aelf_json, AelfHttpError
from utils import json_to_rss
from keys import KEY_TO_OFFICE

CURRENT_VERSION = 28

# List of APIs engines + fallback path
APIS = {
    'json':      [get_office_for_day_api, get_office_for_day_aelf_json],
    'json_only': [get_office_for_day_api],
}

# Office configuration, including API engine and postprocessor
DEFAULT_FALLBACK_LEN_TRESHOLD = 4000 # empty complies are 3600 bytes
OFFICES = {
    "informations": {
        'postprocess': [meta.postprocess],
        'fallback_len_treshold': -1, # There is no fallback for meta
        'api': 'json_only',
    },
    "lectures": {
        'postprocess': [lectures.postprocess],
    },
    "tierce": {
        'postprocess': [],
    },
    "sexte": {
        'postprocess': [],
    },
    "none": {
        'postprocess': [],
    },
    "laudes": {
        'postprocess': [laudes_vepres.postprocess],
    },
    "vepres": {
        'postprocess': [laudes_vepres.postprocess],
    },
    "complies": {
        'postprocess': [],
    },
    "messes": {
        'postprocess': [messes.postprocess],
    },
}

def parse_date_or_abort(date):
    try:
        year, month, day = date.split('-')
        return datetime.date(int(year), int(month), int(day))
    except:
        abort(400)

def return_error(status, message):
    '''
    AELF app does not support codes != 200 (yet), work around this but still keep the intent clear
    '''
    data = u"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <atom:link rel="self" type="application/rss+xml" href="http://rss.aelf.org/rss.php/messe"/>
	<title>Erreur {status} {message}</title>
        <description><![CDATA[(c) Association Épiscopale Liturgique pour les pays francophones - 2016]]></description>
        <link>http://aelf.org</link>
        <pubDate>Mon, 16 May 2016 23:09:21 +0200</pubDate>
        <lastBuildDate>Mon, 16 May 2016 23:09:21 +0200</lastBuildDate>
        <image>
            <title>AELF</title>
            <url>http://aelf.org/images/logo.jpg</url>
            <link>http://aelf.org</link>
        </image>
        <language>fr</language>
        <copyright>Copyright AELF - Tout droits réservés</copyright>
        <item>
            <title>Oups... Cette lecture n'est pas dans notre calendrier ({status})</title>
            <description><![CDATA[
<p>{message}</p>
<p>Saviez-vous que cette application est développée complètement bénévolement&nbsp;? Elle est construite en lien et avec le soutien de l'AELF, mais elle reste un projet indépendant, soutenue par <em>votre</em> prière&nbsp!</p>
<p>Si vous pensez qu'il s'agit d'une erreur, vous pouvez envoyer un mail à <a href="mailto:cathogeek@epitre.co">cathogeek@epitre.co</a>.<p>
	    ]]></description>
        </item>
    </channel>
</rss>"""
    return Response(data.format(status=status, message=message), mimetype='application/rss+xml')


#
# Internal API
#

@app.route('/status')
def get_status():
    # Attempt to get the mass for today. If we can't, we are in trouble
    try:
        mass = do_get_office(CURRENT_VERSION, "messes", *[int(c) for c in (time.strftime("%d:%m:%Y").split(':'))])
    except:
        return "Can not load mass", 500

    if '<source>api</source>' not in mass.data:
        return "Data is not comming from the main API:"+mass.data, 500

    # All good !
    return Response(json.dumps(int(time.time())), mimetype='application/json')

#
# Modern API (beta)
#

@app.route('/<int:version>/office/<office>/<date>')
def get_office(version, office, date):
    date = parse_date_or_abort(date)
    return do_get_office(version, office, date)

def do_get_office(version, office, date):
    data = None
    error = None

    # Validate office name
    if office not in OFFICES:
	return return_error(404, u"Cet office (%s) est inconnu..." % office)

    # Validate API engine
    office_api_engine_name = OFFICES[office].get('api', 'json')
    office_api_engines = APIS.get(office_api_engine_name, None)
    if not office_api_engines:
	return return_error(500, u"Hmmm, où se trouve donc l'office %s ?" % office)

    # Attempt all engines until we find one that works
    last_http_error = None
    for office_api_engine in office_api_engines:
        # Attempt to load
        try:
            data = office_api_engine(office, date)
        except AelfHttpError as http_err:
            last_http_error = http_err
            continue
        except Exception as e:
            last_http_error = AelfHttpError(500, str(e))
            continue

        # Does it look broken ?
        if len(unicode(data)) < OFFICES[office].get('fallback_len_treshold', DEFAULT_FALLBACK_LEN_TRESHOLD):
            last_http_error = AelfHttpError(500, u"L'office est trop court, c'est louche...")
            continue
        break
    else:
        if last_http_error.status == 404:
	    return return_error(404, u"Aucune lecture n'a été trouvée pour cette date.")
        return return_error(last_http_error.status, last_http_error.message)

    # Apply office specific postprocessor
    mode = "beta" if request.args.get('beta', 0) else "prod"
    for postprocessor in OFFICES[office]['postprocess']:
        data = postprocessor(version, mode, data)

    # Return
    rss = json_to_rss(data)
    return Response(rss, mimetype='application/rss+xml')

#
# Legacy API (keep compatible in case fallback is needed)
#

@app.route('/<int:day>/<int:month>/<int:year>/<key>')
def get_office_legacy(day, month, year, key):
    if key not in KEY_TO_OFFICE:
	return return_error(404, "Aucune lecture n'a été trouvée pour cet office.")
    office = KEY_TO_OFFICE[key]
    version = int(request.args.get('version', 0))
    date = datetime.date(year, month, day)
    return do_get_office(version, KEY_TO_OFFICE[key], date)

if __name__ == "__main__":
    if os.environ.get('AELF_DEBUG', False):
        app.debug = True
    app.run(host="0.0.0.0", port=4000)

