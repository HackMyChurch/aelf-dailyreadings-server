# -*- coding: utf-8 -*-

import meta
import messes
import laudes_vepres
import lectures
from lib.exceptions import AelfHttpError
from lib.postprocessor import postprocess_office_pre
from lib.postprocessor import postprocess_office_post
from lib.postprocessor import postprocess_office_html
from lib.input import get_office_for_day_api, get_office_for_day_aelf_json

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
        'should_fallback': messes.should_fallback,
    },
}

def default_should_fallback(version, mode, data):
    office = data['office']
    return len(unicode(data)) < OFFICES[office].get('fallback_len_treshold', DEFAULT_FALLBACK_LEN_TRESHOLD)

def get(version, mode, office, date, region):
    data = None
    error = None

    # Validate office name
    if office not in OFFICES:
	return return_error(404, u"Cet office (%s) est inconnu..." % office)

    # Validate API engine
    office_api_engine_name = OFFICES[office].get('api', 'json')
    office_api_engines = APIS.get(office_api_engine_name, None)
    if not office_api_engines:
	return return_error(500, u"Hmmm, où se trouve donc l'office %s ?" % office)

    # Attempt all engines until we find one that works
    last_http_error = None
    for office_api_engine in office_api_engines:
        # Attempt to load for requested region and 'romain'
        regions = [region] if region == "romain" else [region, 'romain']
        for r in regions:
            # Attempt to load
            try:
                data = office_api_engine(office, date, r)
            except AelfHttpError as http_err:
                last_http_error = http_err
                continue
            except Exception as e:
                last_http_error = AelfHttpError(500, str(e))
                continue

            # Does it look broken ?
            if OFFICES[office].get('should_fallback', default_should_fallback)(version, mode, data):
                last_http_error = AelfHttpError(500, u"L'office est trop court, c'est louche...")
                continue

            # Actually not, this looks OK
            break
        else:
            # We did not break, that means no valid data: let's try the next engine
            continue
        break
    else:
        # Report unrecoverable errors
        if last_http_error.status == 404:
	    return return_error(404, u"Aucune lecture n'a été trouvée pour cette date.")
        return return_error(last_http_error.status, last_http_error.message)

    # Apply office specific postprocessor
    try:
        for postprocessor in OFFICES[office]['postprocess']:
            data = postprocessor(version, mode, data)
    except Exception as e:
        return return_error(500, u"Erreur lors de la génération de l'office.")

    # Return
    return data

def return_error(status, message):
    '''
    AELF app does not support codes != 200 (yet), work around this but still keep the intent clear
    '''
    title = u"<title>Oups... Cette lecture n'est pas dans notre calendrier ({status})</title>"
    description = u"""
<p>{message}</p>
<p>Saviez-vous que cette application est développée complètement bénévolement&nbsp;? Elle est construite en lien et avec le soutien de l'AELF, mais elle reste un projet indépendant, soutenue par <em>votre</em> prière&nbsp!</p>
<p>Si vous pensez qu'il s'agit d'une erreur, vous pouvez envoyer un mail à <a href="mailto:support@epitre.co">support@epitre.co</a>.<p>
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
                        u'title': title.format(status=status),
                        u'text':  description.format(status=status, message=message)
                    },
                ],
            }
        ],
    }

