# -*- coding: utf-8 -*-

import datetime
import meta
import messes
import laudes_vepres
import lectures
from lib.cache import Cache
from lib.exceptions import AelfHttpError
from lib.postprocessor import postprocess_office_pre
from lib.postprocessor import postprocess_office_post
from lib.postprocessor import postprocess_office_html
from lib.input import get_office_for_day_api

# Office configuration, including API engine and postprocessor
OFFICES = {
    "informations": {
        'postprocess': [meta.postprocess],
    },
    "lectures": {
        'postprocess': [postprocess_office_pre, lectures.postprocess, postprocess_office_post],
    },
    "tierce": {
        'postprocess': [postprocess_office_pre, postprocess_office_post],
    },
    "sexte": {
        'postprocess': [postprocess_office_pre, postprocess_office_post],
    },
    "none": {
        'postprocess': [postprocess_office_pre, postprocess_office_post],
    },
    "laudes": {
        'postprocess': [postprocess_office_pre, laudes_vepres.postprocess, postprocess_office_post],
    },
    "vepres": {
        'postprocess': [postprocess_office_pre, laudes_vepres.postprocess, postprocess_office_post],
    },
    "complies": {
        'postprocess': [postprocess_office_pre, postprocess_office_post],
    },
    "messes": {
        'postprocess': [postprocess_office_html, messes.postprocess, postprocess_office_post],
    },
}

cache = Cache()

def get_from_network(version, mode, office_name, date, region):
    data = None
    error = None

    # Validate office name
    if office_name not in OFFICES:
        return return_error(404, "Cet office (%s) est inconnu..." % office_name)

    # Attempt to load
    error = None
    try:
        data = get_office_for_day_api(office_name, date, region)
    except AelfHttpError as http_err:
        # Prepare the error message
        if http_err.status == 404:
            error = return_error(404, "Aucune lecture n'a été trouvée pour cette date.")
        else:
            error = return_error(http_err.status, str(http_err))

        # There is a (tiny) chance that this error is expected, check with the informations
        try:
            data = get_office_for_day_api("informations", date, region)
        except Exception:
            # Immediately return the original error
            return error

    # Apply office specific postprocessor
    for postprocessor in OFFICES[office_name]['postprocess']:
        data = postprocessor(version, mode, data)

    # If we had an error forward it if the variants are still empty
    if error is not None and not data.get('variants'):
        return error

    # Return
    return data

def get(version: int, mode: str, office_name: str, date: datetime.date, region: str) -> tuple[dict, str, datetime.datetime]:
    # Attempt to load from cache
    cache_key = (version, mode, office_name, date, region)
    cache_entry = cache.get(cache_key)
    if cache_entry is None:
        office = get_from_network(version, mode, office_name, date, region)
        cache_entry = cache.set(cache_key, office)

    return cache_entry.value, cache_entry.checksum, cache_entry.date

def return_error(status, message):
    '''
    AELF app does not support codes != 200 (yet), work around this but still keep the intent clear
    '''
    title = "Oups... Cette lecture n'est pas dans notre calendrier ({status})"
    description = """
<p>{message}</p>
<p>Saviez-vous que cette application est développée complètement bénévolement&nbsp;? Elle est construite en lien et avec le soutien de l'AELF, mais elle reste un projet indépendant, soutenue par <em>votre</em> prière&nbsp!</p>
"""

    return {
        'source':  'error',
        'name':    'error',
        'status':  status,
        'message': message,
        'variants': [
            {
                'name': 'message',
                'lectures': [
                    [{
                        'title': title.format(status=status),
                        'text':  description.format(status=status, message=message)
                    }],
                ],
            }
        ],
    }

