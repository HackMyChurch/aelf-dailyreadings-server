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
from utils import get_office_for_day, AelfHttpError
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

#
# Internal API
#

@app.route('/status')
def get_status():
    # Attempt to get the mass for today. If we can't, we are in trouble
    try:
        mass = do_get_office(CURRENT_VERSION, "messe", *(time.strftime("%d:%m:%Y").split(':')))
    except:
        return "Can not load mass", 500

    if '<category>Messe</category>' not in mass.data:
        return "Does not look like mass", 500

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
    try:
        data = get_office_for_day(office, day, month, year)
    except AelfHttpError as http_err:
        return "Failed to load reading", http_err.status

    # Don't want to cache these BUT don't want to break the app either. Should be a 404 though...
    if 'pas dans notre calendrier' in data:
        return Response(data, mimetype='application/rss+xml')

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
        abort(404)
    office = KEY_TO_OFFICE[key]
    version = int(request.args.get('version', 0))
    return do_get_office(version, KEY_TO_OFFICE[key], day, month, year)

if __name__ == "__main__":
    if os.environ.get('AELF_DEBUG', False):
        app.debug = True
    app.run(host="0.0.0.0", port=4000)

