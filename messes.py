import datetime
from utils import fix_case, AELF_SITE

def postprocess_holly_saturday(version, mode, data):
    text = """<p>
    Le Samedi Saint est un jour spécial. C'est le jour de l'attente de la résurrection
    du Christ. Il n'y a pas de messe ce jour là. Si vous cherchez la Veillée Pascale,
    vous la trouverez dans les lectures de Pâques, c'est la première messe.
    </p>"""

    if version >= 29:
        date = data['date']
        date = date + datetime.timedelta(1)
        base_link = AELF_SITE.format(year=date.year, month=date.month, day=date.day, office='messe', region=data['informations']['zone'])
        text += '<div class="app-office-navigation"><a href="%s#messe1_lecture1" class="variant-1">Veillée Pascale</a></div>' % (base_link)

    data['variants'] = [
        {
            'name': 'Samedi saint',
            'lectures': [
                [{
                    'title':     'Messe: Le saviez-vous ?',
                    'text':      text,
                    'reference': '',
                    'key':       '',
                }]
            ]
        }
    ]
    return data

def postprocess_keys(version, mode, data):
    '''
    Rewrite keys to match AELF's website convention
    '''
    messe_counter = 0
    for office_variant in data['variants']:
        messe_counter += 1
        lecture_counter = 0
        for lecture_variants in office_variant['lectures']:
            for lecture in lecture_variants:
                lecture_counter += 1
                lecture['key.orig'] = lecture['key']
                lecture['key'] = "messe%s_lecture%s" % (messe_counter, lecture_counter)

def postprocess_links(version, mode, data):
    '''
    Generate a link page on compatible versions
    '''
    # No support for links in the app, sorry
    if version < 29:
        return data

    # Not applicable if there is a single mass
    if len(data['variants']) < 2:
        return data

    # PASS 1: detect + fix known to be broken cases
    if data['variants'][0]['lectures'][0][0]['key.orig'] == "entree_messianique":
        data['variants'][ 0]['name'] = "Entrée messianique"
        data['variants'][-1]['name'] = "Messe du jour"

    # Fix may friend the all-caps...
    for office_variant in data['variants']:
        office_variant['name'] = fix_case(office_variant['name'])

    # PASS 2: collect the data
    variant_data = [];
    for office_variant in data['variants']:
        variant_data.append({
            'name': office_variant['name'],
            'key':  office_variant['lectures'][0][0]['key'],
        })

    # GENERATE the title slide
    links = ""
    date = data['date']
    base_link = AELF_SITE.format(year=date.year, month=date.month, day=date.day, office='messe', region=data['informations']['zone'])
    for variant_counter, variant in enumerate(variant_data):
        links += '<a href="%s#%s" class="variant-%s">%s</a>' % (base_link, variant['key'], variant_counter, variant['name'])

    # PASS 3: Insert the title slide before each variant
    for variant_counter, variant in enumerate(data['variants']):
        text = links.replace('class="variant-%s"' % variant_counter, 'class="variant-%s active"' % variant_counter)
        variant['lectures'].insert(0, [{
            'title':     'Messes',
            'text':      '<div class="app-office-navigation">%s</div>' % text,
            'reference': '',
            'key':       'navigation',
        }])

def postprocess(version, mode, data):
    if data['informations'].get('jour_liturgique_nom', '').lower().strip() == "samedi saint":
        return postprocess_holly_saturday(version, mode, data)

    postprocess_keys (version, mode, data)
    postprocess_links(version, mode, data)

    return data

