from datetime import datetime


EARLIEST_PUBLISHED = datetime(2016, 1, 1, 0, 0, 0)


def find_title_div(tag):
    return tag.name == "div" and tag.has_attr("class") and "Article_elementTitle__" in tag["class"][0]


def find_published_div(tag):
    return tag.name == "div" and tag.has_attr("class") and "Article_elementPublishdate__" in tag["class"][0]


def find_lead_div(tag):
    return tag.name == "div" and tag.has_attr("class") and "Article_elementLead__" in tag["class"][0]


def find_body_section(tag):
    return tag.name == "section" and tag.has_attr("class") and "Article_body__" in tag["class"][0]


def find_text_divs(tag):
    return tag.name == "div" and tag.has_attr("class") and "Article_elementTextblockarray__" in tag["class"][0]


def index(story_soup, since=None):
    """

    :param story_soup:
    :param since: datetime, only retrieves the story if its newer than the value of this parameter
    :return: a dict representing a story or None if a required field could not be extracted
    """
    title_div = story_soup.find(find_title_div)
    if not title_div: 
        print("No title div")
        return None
    title = title_div.h2.span.next_sibling.string
    if not title: 
        print("No title")
        return None

    published_div = story_soup.find(find_published_div)
    if not published_div: 
        print ("No publish div")
        return None
    
    published_date = published_div.time["datetime"]
    published_date = datetime.strptime(published_date[:16], "%Y-%m-%dT%H:%M")
    if published_date < EARLIEST_PUBLISHED: return None  # only fetch stories newer than 2015
    if since and published_date <= since: return None

    subtitle_div = story_soup.find(find_lead_div)
    if not subtitle_div or not subtitle_div.p:
        print("No lead div")
        return None
    subtitle = subtitle_div.p.string
    if not subtitle: 
        print("No subtitle")
        return None

    body_section = story_soup.find(find_body_section)
    if not body_section:
        print("No body section")
    text = ""
    for text_block in body_section.find_all(find_text_divs):
        if text_block.p.string:
            text += text_block.p.string + "\n"
    if not text:
        print("No text")
        return None

    return {
        "title": title,
        "subtitle": subtitle,
        "text": text,
        "published": published_date
        }


if __name__ == "__main__":
    print(
        index(["http://www.20_min.ch/schweiz/news/story/Zwei-Kamele-beunruhigten-die-Davoser-23118818"])[0]["published"])