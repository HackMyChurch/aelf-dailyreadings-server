# -*- coding: utf-8 -*-

import time
import threading
import datetime

from office_controller import get as do_get_office, OFFICES
from lib.constants import CURRENT_VERSION, STATUS_DAYS_TO_MONITOR, STATUS_DAYS_404_FATAL, STATUS_PROBE_INTERVAL

REASON_OK="OK"
REASON_WARN="WARN"
REASON_ERROR="ERROR"

HTML_STATUS = {
    REASON_OK:    "success",
    REASON_WARN:  "warning",
    REASON_ERROR: "danger",
}

_runner = None
_status = {
    'offices': {},
    'status': 200,
}

#
# Internal machinery
#

def validate_office(office, days_ahead):
    reason = (REASON_OK, "")
    message = office.get('message', '')

    # Validate there is no encoded / catched error
    if office['source'] == "error":
        if office.get('status', -1) == 404 and days_ahead < STATUS_DAYS_404_FATAL:
            reason = (REASON_WARN, message if message else 'Missing office')
        else:
            return REASON_ERROR, "Invalid API source - " + message

    # Validate optimal data source
    if office['source'] != "api":
        reason = (REASON_WARN, "Degraded API source")

    # Validate there is at least 1 lectures
    if len(office['variants'][0]['lectures']) < 1:
        return REASON_ERROR, "Empty office"

    return reason

def validate_future_offices():
    '''
    Loop over upcomming STATUS_DAYS_TO_MONITOR days and OFFICES and make sure they are valid
    '''
    global _status
    status = {}
    status_code = 200

    date = datetime.date.today()
    for days_ahead in range(STATUS_DAYS_TO_MONITOR):
        date += datetime.timedelta(days=1)
        date_str = str(date)
        status[date_str] = {}
        for office_name in OFFICES.keys():
            try:
                office = do_get_office(CURRENT_VERSION, "prod", office_name, date, "romain")
                reason = validate_office(office, days_ahead)
            except Exception as e:
                reason = (REASON_ERROR, str(e))

            if reason[0] == REASON_ERROR:
                status_code = 500

            status[date_str][office_name] = reason

    # Commit
    _status = {
        'offices': status,
        'status': status_code,
    }

def runner():
    try:
        validate_future_offices()
    except Exception as e:
        print "Failed to validate status: "+str(e)
    time.sleep(STATUS_PROBE_INTERVAL)

#
# Public API
#

def get_status_data():
    return _status

def init():
    '''
    Start monitoring thread.
    FIXME: add a lock ?
    '''
    global _runner
    if _runner is not None:
        return

    _runner = threading.Thread(target=runner)
    _runner.daemon = True
    _runner.start()
    

