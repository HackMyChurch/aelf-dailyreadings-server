#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Response, abort
app = Flask(__name__)

import os
import meta
from utils import get_office_for_day

POST_PROCESSORS = {
    "meta": meta.postprocess,
}

def parse_date_or_abort(date):
    try:
        year, month, day = date.split('-')
        return int(year), int(month), int(day)
    except:
        abort(400)

@app.route('/v0/office/<office>/<date>')
def get_office(office, date):
    year, month, day = parse_date_or_abort(date)
    data = get_office_for_day(office, day, month, year)

    # Don't want to cache these BUT don't want to break the app either. Should be a 404 though...
    if 'pas dans notre calendrier' in data:
        return Response(data, mimetype='application/rss+xml')

    # Do we have a secret way to enhance this ?
    if office in POST_PROCESSORS:
        data = POST_PROCESSORS[office](data)

    # Return
    return Response(data, mimetype='application/rss+xml')

if __name__ == "__main__":
    if os.environ.get('AELF_DEBUG', False):
        app.debug = True
    app.run(host="0.0.0.0", port=4000)

