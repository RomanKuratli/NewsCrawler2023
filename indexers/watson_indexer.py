from datetime import datetime


EARLIEST_PUBLISHED = datetime(2016, 1, 1, 0, 0, 0)


def find_story_div(tag):
    return tag.name == "div" and tag.has_attr("class") and "story" in tag["class"]


def find_title(tag):
    return tag.name == "h2" and tag.has_attr("class") and tag["class"][0] == "watson-snippet__title"


def find_publish_date_icon_span(tag):
    return tag.name == "span" and tag.has_attr("class") and "watson-snippet__shareBubbles__published" in tag["class"]


def find_text_tags(tag):
    return tag.name == "p" and tag.has_attr("class") and "watson-snippet__text" in tag["class"]


def index(story_soup, since=None):
    """

    :param story_soup:
    :param since: datetime, only retrieves the story if its newer than the value of this parameter
    :return: a dict representing a story or None if a required field could not be extracted
    """
    story_div = story_soup.find(find_story_div)
    if not story_div:
        return None

    title = story_div.find(find_title)
    if not title: 
        return None
    title_txt = title.string

    publish_icon = story_div.find(find_publish_date_icon_span)
    if not publish_icon: 
        return None
    changed_date = publish_icon.next_sibling.string.strip()
    changed_date = datetime.strptime(changed_date, "%d.%m.%Y, %H:%M")
    if changed_date < EARLIEST_PUBLISHED: 
        return None  # only fetch stories newer than 2015
    if since and changed_date <= since: 
        return None

    text_tags = story_div.find_all(find_text_tags)
    if not text_tags:
        return None

    # Treat the first paragraph as lead text
    subtitle = text_tags[0].string
    text = ""
    for text_content in text_tags[1:]:
        if text_content.string:
            text += text_content.string + "\n"
    

    return {
        "title": title_txt,
        "subtitle": subtitle,
        "text": text,
        "published": changed_date
        }


if __name__ == "__main__":
    from utils.utils import make_soup
    story_soup = make_soup("https://www.watson.ch/schweiz/bundesrat/457981257-bundesrat-roesti-beantragt-ukw-verlaengerung-bis-ende-2026")
    assert story_soup, "Could not make soup!"
    print(index(story_soup))