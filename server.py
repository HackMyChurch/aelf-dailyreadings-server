#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Response, abort, request, jsonify
from raven.contrib.flask import Sentry
app = Flask(__name__)
sentry = Sentry()

import os
import time
import json
import meta
import messes
import laudes_vepres
import lectures
import datetime
from lib.input import get_office_for_day_api, get_office_for_day_aelf_json
from lib.exceptions import AelfHttpError
from lib.postprocessor import postprocess_office_common
from lib.postprocessor import postprocess_office_html
from lib.output import office_to_json, office_to_rss
from lib.constants import DEFAULT_REGION
from keys import KEY_TO_OFFICE, SENTRY_DSN

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
        'postprocess': [postprocess_office_common, lectures.postprocess],
    },
    "tierce": {
        'postprocess': [postprocess_office_common],
    },
    "sexte": {
        'postprocess': [postprocess_office_common],
    },
    "none": {
        'postprocess': [postprocess_office_common],
    },
    "laudes": {
        'postprocess': [postprocess_office_common, laudes_vepres.postprocess],
    },
    "vepres": {
        'postprocess': [postprocess_office_common, laudes_vepres.postprocess],
    },
    "complies": {
        'postprocess': [postprocess_office_common],
    },
    "messes": {
        'postprocess': [postprocess_office_html, messes.postprocess],
        'should_fallback': messes.should_fallback,
    },
}

def default_should_fallback(version, mode, data):
    office = data['office']
    return len(unicode(data)) < OFFICES[office].get('fallback_len_treshold', DEFAULT_FALLBACK_LEN_TRESHOLD)

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
    title = u"<title>Oups... Cette lecture n'est pas dans notre calendrier ({status})</title>"
    description = u"""
<p>{message}</p>
<p>Saviez-vous que cette application est développée complètement bénévolement&nbsp;? Elle est construite en lien et avec le soutien de l'AELF, mais elle reste un projet indépendant, soutenue par <em>votre</em> prière&nbsp!</p>
<p>Si vous pensez qu'il s'agit d'une erreur, vous pouvez envoyer un mail à <a href="mailto:cathogeek@epitre.co">cathogeek@epitre.co</a>.<p>
"""

    return {
        u'source':  u'error',
        u'name':    u'error',
        u'status':  status,
        u'message': message,
        u'variants': [
            {
                u'name': u'message',
                u'lectures': [
                    {
                        u'title':       title.format(status=status),
                        u'description': description.format(status=status, message=message)
                    },
                ],
            }
        ],
    }

#
# Internal API
#

@app.route('/status')
def get_status():
    # Attempt to get the mass for today. If we can't, we are in trouble
    try:
        mass = do_get_office(CURRENT_VERSION, "messes", datetime.date(*[int(c) for c in (time.strftime("%Y:%m:%d").split(':'))]))
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
    region = request.args.get('region', DEFAULT_REGION)
    rss = office_to_rss(do_get_office(version, office, date, region))
    return Response(rss, mimetype='application/rss+xml')

@app.route('/<int:version>/office/<office>/<date>.json')
def get_office_json(version, office, date):
    date = parse_date_or_abort(date)
    region = request.args.get('region', DEFAULT_REGION)
    return jsonify(office_to_json(do_get_office(version, office, date, region)))

def do_get_office(version, office, date, region):
    mode = "beta" if request.args.get('beta', 0) else "prod"
    data = None
    error = None

    sentry_data = {
        'application': version,
        'office': office,
        'date': date,
    }

    # Validate office name
    if office not in OFFICES:
        sentry.captureMessage("Invalid office", extra=sentry_data);
	return return_error(404, u"Cet office (%s) est inconnu..." % office)

    # Validate API engine
    office_api_engine_name = OFFICES[office].get('api', 'json')
    office_api_engines = APIS.get(office_api_engine_name, None)
    if not office_api_engines:
        sentry.captureMessage("Missing office engine", extra=sentry_data);
	return return_error(500, u"Hmmm, où se trouve donc l'office %s ?" % office)

    # Attempt all engines until we find one that works
    last_http_error = None
    for office_api_engine in office_api_engines:
        # Attempt to load
        try:
            data = office_api_engine(office, date, region)
        except AelfHttpError as http_err:
            sentry.captureException(extra=sentry_data)
            last_http_error = http_err
            continue
        except Exception as e:
            sentry.captureException(extra=sentry_data)
            last_http_error = AelfHttpError(500, str(e))
            continue

        # Does it look broken ?
        if OFFICES[office].get('should_fallback', default_should_fallback)(version, mode, data):
            sentry.captureMessage("Office is too short, triggering fallback", extra=sentry_data);
            last_http_error = AelfHttpError(500, u"L'office est trop court, c'est louche...")
            continue
        break
    else:
        if last_http_error.status == 404:
	    return return_error(404, u"Aucune lecture n'a été trouvée pour cette date.")
        return return_error(last_http_error.status, last_http_error.message)

    # Apply office specific postprocessor
    try:
        for postprocessor in OFFICES[office]['postprocess']:
            data = postprocessor(version, mode, data)
    except Exception as e:
        sentry.captureException(extra=sentry_data)
        return return_error(500, u"Erreur lors de la génération de l'office.")

    # Return
    return data

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
    rss = office_to_rss(do_get_office(version, KEY_TO_OFFICE[key], date, region))
    return Response(rss, mimetype='application/rss+xml')

if __name__ == "__main__":
    if os.environ.get('AELF_DEBUG', False):
        app.debug = True

    # Init Sentry
    if app.debug:
        sentry.init_app(app)
    else:
        sentry.init_app(app, dsn=SENTRY_DSN)
    app.run(host="0.0.0.0", port=4000)

