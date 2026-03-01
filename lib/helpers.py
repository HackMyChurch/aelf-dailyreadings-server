import datetime


def build_link(
    office: str, region: str, date: datetime.date, variant: int, lecture: int
) -> str:
    return f"http://www.aelf.org/{date.isoformat()}/{region}/{office}#{office}{variant}_lecture{lecture}"


def build_button(
    title: str,
    office: str,
    region: str,
    date: datetime.date,
    variant: int,
    lecture: int,
) -> str:
    return f'<div class="app-office-navigation"><a href="{build_link(office, region, date, variant, lecture)}" class="variant-1">{title}</a></div>'
