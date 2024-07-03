from xml.sax.saxutils import escape
from copy import deepcopy

def office_to_json(version, data):
    '''
    Take an office dict and serialize any non json data so that jsonify can
    return a valid json.
    '''
    data = deepcopy(data)
    if 'date' in data:
        data['date'] = data['date'].isoformat()
    return data

def office_to_rss(version, data):
    '''
    API and json scrappers return a json of the form:
    ```json
    {
        "informations": {},
        "variants": [
            [{
                "name": OFFICE_NAME,
                "lectures": [
                    {
                        "title":     "",
                        "reference": "",
                        "text":      "",
                        "antienne":  "", // Optional
                        "verset":    "", // Optional
                        "repons":    "", // Optional
                        "key":       "",
                    },
                ],
            }],
            [{
                "name": OFFICE_VARIANTE_NAME,
                "lectures": []
            }]
        ]
    }
    ```

    When multiple alternatives are proposed for an office (typically the mass), chain them and
    add a <variant> with the "OFFICE_NAME" key in the items
    '''
    out = []
    out.append('''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <language>fr</language>
        <source>%s</source>
''' % data.get('source', 'unk'))

    for office_variant in data.get('variants', []):
        office = office_variant['name']
        for lecture_variants in office_variant['lectures']:
            lecture = lecture_variants[0]

            key = lecture.get('key', '')
            text = lecture.get('text', '')
            title = lecture.get('title', '')
            reference = lecture.get('reference', '')

            out.append('''
            <item>
                <variant>{office}</variant>
                <title>{title}</title>
                <reference>{reference}</reference>
                <key>{key}</key>
                <description><![CDATA[{text}]]></description>
            </item>'''.format(
                office    = office,
                title     = escape(title),
                reference = escape(reference),
                key       = escape(key),
                text      = text,
            ))

    out.append('''</channel></rss>''')
    return ''.join(out)
