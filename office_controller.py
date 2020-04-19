# -*- coding: utf-8 -*-

import meta
import messes
import laudes_vepres
import lectures
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

def get(version, mode, office, date, region):
    data = None
    error = None

    # Validate office name
    if office not in OFFICES:
        return return_error(404, "Cet office (%s) est inconnu..." % office)

    # Attempt to load
    try:
        data = get_office_for_day_api(office, date, region)
    except AelfHttpError as http_err:
        if http_err.status == 404:
            return return_error(404, "Aucune lecture n'a été trouvée pour cette date.")
        return return_error(http_err.status, str(http_err))

    # Apply office specific postprocessor
    for postprocessor in OFFICES[office]['postprocess']:
        data = postprocessor(version, mode, data)

    # Return
    return data

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

