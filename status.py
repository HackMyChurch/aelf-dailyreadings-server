# -*- coding: utf-8 -*-

import time
import threading
import datetime

from office_controller import get as do_get_office, OFFICES
from lib.constants import CURRENT_VERSION, STATUS_DAYS_TO_MONITOR, STATUS_DAYS_404_FATAL, STATUS_PROBE_INTERVAL, STATUS_PROBE_INTERVAL_ERROR

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
    'date': 'in progress...',
    'message': '',
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
    for days_ahead in range(STATUS_DAYS_TO_MONITOR):
        _status['message'] = 'Refreshing day %s of %d. Please wait.' % (days_ahead+1, STATUS_DAYS_TO_MONITOR)
        date = datetime.date.today()
        date += datetime.timedelta(days=days_ahead)
        date_str = str(date)
        day_status = {}
        for office_name in OFFICES.keys():
            url = "/%s/office/%s/%s.json" % (CURRENT_VERSION, office_name, date_str)
            try:
                office = do_get_office(CURRENT_VERSION, "prod", office_name, date, "romain")
                reason = validate_office(office, days_ahead)
            except Exception as e:
                reason = (REASON_ERROR, str(e))

            if reason[0] == REASON_ERROR:
                _status['status'] = 500

            day_status[office_name] = reason[0], reason[1], url
        _status['offices'][date_str] = day_status

    # All done !
    _status['message'] = ''
    _status['status'] = 200
    _status['date'] = str(datetime.datetime.today())

def runner():
    while True:
        next_sleep_interval = STATUS_PROBE_INTERVAL
        try:
            validate_future_offices()
        except Exception as e:
            _status['message'] = "Failed to validate status: "+str(e)
            _status['status'] = 500
            next_sleep_interval = STATUS_PROBE_INTERVAL_ERROR

        if _status['status'] != 200:
            next_sleep_interval = STATUS_PROBE_INTERVAL_ERROR

        time.sleep(next_sleep_interval)

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
    

