def postprocess(version, mode, data):
    data['variants'] = [
        {
            'name': 'Informations',
            'lectures': [
                [{
                    'title':     'Jour liturgique',
                    'text':      data['informations']['text'],
                    'reference': '',
                    'key':       'informations',
                }]
            ]
        }
    ]

    return data

