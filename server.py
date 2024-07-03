#!/usr/bin/env python

from flask import Flask, Response, abort, request, jsonify, render_template
app = Flask(__name__)

import os
import json
import datetime
from lib.output import office_to_json, office_to_rss
from lib.constants import DEFAULT_REGION, CURRENT_VERSION
from office_controller import get as do_get_office, get_from_network as do_get_office_from_network, OFFICES
import status

if os.environ.get('AELF_DEBUG', False):
    app.debug = True

#
# Init
#

status.init()

#
# Utils
#

def parse_date_or_abort(date) -> datetime.date:
    try:
        year, month, day = date.split('-')
        return datetime.date(int(year), int(month), int(day))
    except:
        abort(400, "Invalid date")

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
        mass = do_get_office_from_network(CURRENT_VERSION, "prod", "messes", datetime.date.today(), 'romain')
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
# Office API, common path
#


def get_deprecation_response(version, format):
    office = {
        "source": "error",
        "name": "error",
        "status": 404,
        "message": "This version of the application is no longer supported",
        "variants": [
            {
                "name": "message",
                "lectures": [
                    [
                        {
                            "title": "Erreur",
                            "text": """
                                <p>Cette version n'est plus supportée</p>
                                <p>Pour continuer à utiliser l'application, merci de la <em>mettre à jour</em> depuis le "Play Store".</p>
                            """,
                        }
                    ],
                ],
            }
        ],
    }

    if format == 'rss':
        return Response(office_to_rss(version, office), mimetype="application/rss+xml")
    else:
        return jsonify(office_to_json(version, office))


def get_office_response(version, office, date, format):
    # Load common params
    mode = "beta" if request.args.get('beta', 0) else "prod"
    region = request.args.get('region', DEFAULT_REGION)

    office, etag, generation_date = do_get_office(version, mode, office, date, region)

    # Cached version is the same as the requested version
    if etag in request.if_none_match:
        return Response(status=304)

    # Generate response
    if format == 'json':
        response = jsonify(office_to_json(version, office))
    else:
        raise ValueError("Invalid format %s" % format)

    response.set_etag(etag)
    response.last_modified = generation_date
    return response

#
# Modern API
#

@app.route('/<int:version>/offices/metadata/<from_date>/<int:days>d')
def get_office_checksums(version, from_date, days):
    from_date = parse_date_or_abort(from_date)
    mode = "beta" if request.args.get('beta', 0) else "prod"
    region = request.args.get('region', DEFAULT_REGION)

    if days < 1 or days > 7:
        abort(400, "Invalid duration")
    
    checksums = {}
    for i in range(days):
        date = from_date + datetime.timedelta(days=i)
        days_checksum = {}
        for office in OFFICES:
            _, checksum, generation_date = do_get_office(version, mode, office, date, region)
            days_checksum[office] = {
                'checksum': checksum,
                'generation-date': generation_date.isoformat(),
            }
        checksums[date.isoformat()] = days_checksum

    return checksums

@app.route('/<int:version>/office/<office>/<date>')
@app.route('/<int:version>/office/<office>/<date>.rss')
def get_office_rss(version, office, date):
    return get_deprecation_response(version, 'rss')


@app.route('/<int:version>/office/<office>/<date>.json')
def get_office_json(version, office, date):
    date = parse_date_or_abort(date)
    return get_office_response(version, office, date, 'json')

#
# Legacy API (keep compatible in case fallback is needed)
#

@app.route('/<int:day>/<int:month>/<int:year>/<key>')
def get_office_legacy(day, month, year, key):
    version = int(request.args.get('version', 0))
    return get_deprecation_response(version, 'rss')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)

