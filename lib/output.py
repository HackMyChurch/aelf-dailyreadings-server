# -*- coding: utf-8 -*-

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
            {
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
            },
            {
                "name": OFFICE_VARIANTE_NAME,
                "lectures": []
            }
        ]
    }
    ```

    When multiple alternatives are proposed for an office (typically the mass), chain them and
    add a <variant> with the "OFFICE_NAME" key in the items
    '''
    out = []
    out.append(u'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <language>fr</language>
        <source>%s</source>
        <copyright>Copyright AELF - Tout droits réservés</copyright>
''' % data.get('source', 'unk'))

    for variant in data.get('variants', []):
        office   = variant['name']
        lectures = variant['lectures']
        for lecture in lectures:
            text = lecture.get('text', '')
            title = lecture.get('title', '')
            reference = lecture.get('reference', '')

            if 'antienne' in lecture:
                text = u"<blockquote><b>Antienne&nbsp;:</b>%s</blockquote>%s" % (lecture['antienne'], text)
            if 'verset' in lecture:
                text = u"%s<blockquote>%s</blockquote>" % (text, lecture['verset'])
            if 'repons' in lecture:
                text = u"%s<blockquote>%s</blockquote>" % (text, lecture['repons'])

            if version >= 47:
                # Build slide title
                long_title = title
                chunks = title.split(':', 1)
                if len(chunks) == 2:
                    title = chunks[0]
                    if chunks[1].strip() == reference.strip():
                        long_title = chunks[0]
                    else:
                        long_title = chunks[1]

                # Prepare reference, if any
                title_reference = u""
                if reference:
                    title_reference = u"<small><i>— %s</i></small>" % (reference)

                # Inject title
                text = "<h3>%s%s</h3><div style=\"clear: both;\"></div>%s" % (long_title, title_reference, text)

            out.append(u'''
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
                key       = escape(lecture.get('key', '')),
                text      = text,
            ))

    out.append(u'''</channel></rss>''')
    return u''.join(out)
