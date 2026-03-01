from lib.input import get_asset
from utils import get_lecture_variants_by_type, insert_lecture_variants_before
from lib.postprocessor import postprocess_office_html_lecture
from lib.helpers import build_button


def postprocess_easter(version, mode, data):
    data["source"] = "api"
    data["variants"] = get_asset("office/lectures/easter")
    data["variants"][0]["lectures"][0][0]["text"] += build_button(
        title="Veillée Pascale",
        office="messe",
        region=data["informations"]["zone"],
        date=data["date"],
        variant=1,
        lecture=1,
    )
    return data


def postprocess(version, mode, data):
    date = data["date"]
    if (
        data["informations"].get("liturgical_period", "") == "triduum"
        and date.isoweekday() == 7
    ):
        return postprocess_easter(version, mode, data)

    # Do not enable postprocessing for versions before 20, unless beta mode
    if mode != "beta" and version < 20:
        return data

    te_deum_item = get_lecture_variants_by_type(data, "office_te_deum")
    lecture_item = get_lecture_variants_by_type(data, "office_lecture")
    oraison_item = get_lecture_variants_by_type(data, "office_oraison")

    # Fix missing "Te Deum" on Sunday, unless careme
    if te_deum_item is not None:
        te_deum = get_asset("prayers/te-deum")
        te_deum_item.lectureVariants[0]["text"] = te_deum["body"]
        postprocess_office_html_lecture(version, mode, te_deum_item.lectureVariants[0])
    elif (
        te_deum_item is None
        and oraison_item
        and date.isoweekday() == 7
        and data["informations"].get("temps_liturgique", "") != "careme"
    ):
        te_deum = get_asset("prayers/te-deum")
        te_deum_lecture = {
            "title": te_deum["title"],
            "text": te_deum["body"],
            "reference": "",
            "key": "te_deum",
        }
        postprocess_office_html_lecture(version, mode, te_deum_lecture)
        insert_lecture_variants_before(data, [te_deum_lecture], oraison_item)

    # Fix oraison slide title: there is no benediction
    if oraison_item is not None:
        oraison_item.lectureVariants[0]["title"] = "Oraison"

    # All done
    return data
