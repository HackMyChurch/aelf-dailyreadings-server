#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Response, abort, request, jsonify, render_template
app = Flask(__name__)

import os
import time
import json
import datetime
import office_controller
from lib.output import office_to_json, office_to_rss
from lib.constants import DEFAULT_REGION, CURRENT_VERSION
from lib.cache import Cache
from keys import KEY_TO_OFFICE
from office_controller import get as do_get_office, return_error, OFFICES
import status

if os.environ.get('AELF_DEBUG', False):
    app.debug = True

#
# Init
#

status.init()
cache = Cache()

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
@app.route('/status.<format>')
def get_status(format="json"):
    status_data = status.get_status_data()
    status_code = status_data['status']
    status_message = status_data['message']

    # Attempt to get the mass for today. If we can't, we are in trouble
    try:
        mass = do_get_office(CURRENT_VERSION, "prod", "messes", datetime.date(*[int(c) for c in (time.strftime("%Y:%m:%d").split(':'))]), 'romain')
        source = mass.get('source', '')
        if source != 'api':
            status_message = "Mass office should come from API. Got: %s" % (source)
            status_code = 500
    except:
        status_message = "Can not load mass"
        status_code = 500

    # All good !
    response = {
        'status': status_code,
        'message': status_message,
        'offices': status_data['offices'],
        'date': status_data['date'],
        'office_names': list(OFFICES.keys()),
    }
    if format == "html":
        return Response(status = status_code, response=render_template('status.html', **response))
    else:
        return Response(status = status_code, response=json.dumps(response), mimetype='application/json')

@app.route('/robots.txt')
def get_robots():
    return Response("User-agent: *\nDisallow: /\n", mimetype='text/plain')

#
# Batch API
#

@app.route('/batch', methods=['POST'])
def batch():
    """
    Execute multiple requests, submitted as a batch.
    source: http://flask.pocoo.org/snippets/131/

    :statuscode 207: Multi status
    """
    try:
        requests = json.loads(request.data)
    except ValueError as e:
        abort(400)

    responses = []

    for index, req in enumerate(requests):
        method = req['method']
        path = req['path']
        body = req.get('body', None)
        headers = req.get('headers', None)

        with app.app_context():
            with app.test_request_context(path, method=method, data=body, headers=headers):
                try:
                    # Pre process Request
                    rv = app.preprocess_request()

                    if rv is None:
                        # Main Dispatch
                        rv = app.dispatch_request()

                except Exception as e:
                    rv = app.handle_user_exception(e)

                response = app.make_response(rv)

                # Post process Request
                response = app.process_response(response)

        # Build complete response
        responses.append({
            "status": response.status_code,
            "response": response.data.decode('utf8'),
            "headers": dict(response.headers),
        })

    return Response(json.dumps(responses), status=207, mimetype="application/json")

#
# Office API, common path
#

def get_office(version, office, date, format):
    # Load common params
    mode = "beta" if request.args.get('beta', 0) else "prod"
    region = request.args.get('region', DEFAULT_REGION)
    etag_remote = request.headers.get('If-None-Match', None)

    # Attempt to load from cache
    cache_key = (version, mode, office, date, region)
    cache_entry = cache.get(cache_key, checksum=etag_remote)
    if cache_entry is not None:
        office = cache_entry.value
        etag_local = cache_entry.checksum
    else:
        office = do_get_office(version, mode, office, date, region)
        etag_local = cache.set(cache_key, office)

    # Cached version is the same as the requested version
    if etag_remote == etag_local:
        return Response(status=304)

    # Generate response
    if format == 'rss':
        response = Response(office_to_rss(version, office), mimetype='application/rss+xml')
    elif format == 'json':
        response = jsonify(office_to_json(version, office))
    else:
        raise ValueError("Invalid format %s" % format)

    response.headers['ETag'] = etag_local
    return response

#
# Modern API (beta)
#

@app.route('/<int:version>/office/<office>/<date>')
@app.route('/<int:version>/office/<office>/<date>.rss')
def get_office_rss(version, office, date):
    date = parse_date_or_abort(date)
    return get_office(version, office, date, 'rss')

@app.route('/<int:version>/office/<office>/<date>.json')
def get_office_json(version, office, date):
    date = parse_date_or_abort(date)
    return get_office(version, office, date, 'json')

#
# Legacy API (keep compatible in case fallback is needed)
#

@app.route('/<int:day>/<int:month>/<int:year>/<key>')
def get_office_legacy(day, month, year, key):
    if key not in KEY_TO_OFFICE:
        return office_to_rss(return_error(404, "Aucune lecture n'a été trouvée pour cet office."))
    office = KEY_TO_OFFICE[key]
    version = int(request.args.get('version', 0))
    date = datetime.date(year, month, day)
    return get_office(version, office, date, 'rss')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)

