#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Response, abort, request
app = Flask(__name__)

import os
import time
import json
import meta
import laudes
import vepres
import complies
import lectures
from utils import get_office_for_day, get_office_for_day_aelf_to_rss, AelfHttpError
from utils import lectures_soup_common_cleanup
from keys import KEY_TO_OFFICE

CURRENT_VERSION = 23

POST_PROCESSORS = {
    "meta": meta.postprocess,
    "laudes": laudes.postprocess,
    "vepres": vepres.postprocess, # TODO: could be enabled for older versions too
    "complies": complies.postprocess, # TODO: could be enabled for older versions too
    "lectures": lectures.postprocess,
}

def parse_date_or_abort(date):
    try:
        year, month, day = date.split('-')
        return int(year), int(month), int(day)
    except:
        abort(400)

def return_error(status, message):
    '''
    AELF app does not support codes != 200 (yet), work around this but still keep the intent clear
    '''
    data = """<?xml version="1.0" encoding="UTF-8"?>
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
        mass = do_get_office(CURRENT_VERSION, "messe", *[int(c) for c in (time.strftime("%d:%m:%Y").split(':'))])
    except:
        return "Can not load mass", 500

    if 'https://rss.aelf.org/messe' not in mass.data:
        return "Does not look like mass\n"+mass.data, 500

    # All good !
    return Response(json.dumps(int(time.time())), mimetype='application/json')

#
# Modern API (beta)
#

@app.route('/<int:version>/office/<office>/<date>')
def get_office(version, office, date):
    year, month, day = parse_date_or_abort(date)
    return do_get_office(version, office, day, month, year)

def do_get_office(version, office, day, month, year):
    data = None
    error = None
    try:
        data = get_office_for_day(office, day, month, year)
    except AelfHttpError as http_err:
        error = http_err

    # Yet another ugly heuristic + fallback
    if data is None or len(data) < 3000:
        try:
            print "[WARN][{office}][{date}] Fallback to scrapping".format(date='%d-%02d-%02d' % (year, month, day), office=office)
            data = get_office_for_day_aelf_to_rss(office, day, month, year)
        except AelfHttpError as http_err:
	    return return_error(http_err.status, "Une erreur s'est produite en chargeant la lecture.")

    # Attempt common cleanup
    try:
        data = lectures_soup_common_cleanup(data)
    except:
        raise
        pass

    # Don't want to cache these BUT don't want to break the app either. Should be a 404 though...
    if 'pas dans notre calendrier' in data:
	return return_error(404, "Aucune lecture n'a été trouvée pour cette date.")

    # Do we have a secret way to enhance this ?
    variant = "beta" if request.args.get('beta', 0) else "prod"
    if office in POST_PROCESSORS:
        data = POST_PROCESSORS[office](version, variant, data, day, month, year)

    # Return
    return Response(data, mimetype='application/rss+xml')

#
# Legacy API (keep compatible in case fallback is needed)
#

@app.route('/<int:day>/<int:month>/<int:year>/<key>')
def get_office_legacy(day, month, year, key):
    if key not in KEY_TO_OFFICE:
	return return_error(404, "Aucune lecture n'a été trouvée pour cet office.")
    office = KEY_TO_OFFICE[key]
    version = int(request.args.get('version', 0))
    return do_get_office(version, KEY_TO_OFFICE[key], day, month, year)

if __name__ == "__main__":
    if os.environ.get('AELF_DEBUG', False):
        app.debug = True
    app.run(host="0.0.0.0", port=4000)

