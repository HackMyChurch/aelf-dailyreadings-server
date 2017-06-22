#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Response, abort, request, jsonify
from raven.contrib.flask import Sentry
app = Flask(__name__)
sentry = Sentry()

import os
import time
import json
import datetime
import office_controller
from lib.output import office_to_json, office_to_rss
from lib.constants import DEFAULT_REGION, CURRENT_VERSION
from keys import KEY_TO_OFFICE, SENTRY_DSN
from office_controller import get as do_get_office, return_error

#
# Init sentry
#

if os.environ.get('AELF_DEBUG', False):
    app.debug = True

if app.debug:
    sentry.init_app(app)
else:
    sentry.init_app(app, dsn=SENTRY_DSN)

office_controller.sentry = sentry

#
# Utils
#

def parse_date_or_abort(date):
    try:
        year, month, day = date.split('-')
        return datetime.date(int(year), int(month), int(day))
    except:
        abort(400)

#
# Internal API
#

@app.route('/status')
def get_status():
    # Attempt to get the mass for today. If we can't, we are in trouble
    try:
        mass = do_get_office(CURRENT_VERSION, "prod", "messes", datetime.date(*[int(c) for c in (time.strftime("%Y:%m:%d").split(':'))]), 'romain')
    except:
        return "Can not load mass", 500

    source = mass.get('source', '')
    if source != 'api':
        return "Mass office should come from API. Got: %s" % (source), 500

    # All good !
    return Response(json.dumps(int(time.time())), mimetype='application/json')

@app.route('/robots.txt')
def get_robots():
    return Response("User-agent: *\nDisallow: /\n", mimetype='text/plain')

#
# Modern API (beta)
#

@app.route('/<int:version>/office/<office>/<date>')
@app.route('/<int:version>/office/<office>/<date>.rss')
def get_office_rss(version, office, date):
    date = parse_date_or_abort(date)
    mode = "beta" if request.args.get('beta', 0) else "prod"
    region = request.args.get('region', DEFAULT_REGION)
    rss = office_to_rss(do_get_office(version, mode, office, date, region))
    return Response(rss, mimetype='application/rss+xml')

@app.route('/<int:version>/office/<office>/<date>.json')
def get_office_json(version, office, date):
    date = parse_date_or_abort(date)
    mode = "beta" if request.args.get('beta', 0) else "prod"
    region = request.args.get('region', DEFAULT_REGION)
    return jsonify(office_to_json(do_get_office(version, mode, office, date, region)))

#
# Legacy API (keep compatible in case fallback is needed)
#

@app.route('/<int:day>/<int:month>/<int:year>/<key>')
def get_office_legacy(day, month, year, key):
    if key not in KEY_TO_OFFICE:
	return return_error(404, "Aucune lecture n'a été trouvée pour cet office.")
    office = KEY_TO_OFFICE[key]
    version = int(request.args.get('version', 0))
    region = request.args.get('region', DEFAULT_REGION)
    date = datetime.date(year, month, day)
    mode = "beta" if request.args.get('beta', 0) else "prod"
    rss = office_to_rss(do_get_office(version, mode, KEY_TO_OFFICE[key], date, region))
    return Response(rss, mimetype='application/rss+xml')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)

