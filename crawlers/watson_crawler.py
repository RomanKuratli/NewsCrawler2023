#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List


def find_wrapper(tag):
    if tag.name == "div" and tag.has_attr("class") and "wrapper" in tag["class"]:
        return True
    return False


def find_teaserlink(tag):
    if tag.name == "a" and tag.has_attr("class") and "teaserlink" in tag["class"]:
        return True
    return False

def crawl(base_link, sec_soup) -> List[str]:
    story_urls = set()
    wrapper = sec_soup.find(find_wrapper)
    for teaserlink in wrapper.find_all(find_teaserlink):
        story_urls.add(teaserlink["href"])
    story_urls = {url for url in story_urls}
    return list(story_urls)


if __name__ == "__main__":
    from utils import make_soup
    soup = make_soup("http://www.watson.ch/Wirtschaft")
    assert soup, "Couldn't make soup!"
    urls = crawl("http://www.watson.ch", soup)
    for url in urls:
        print(url)
    print(str(len(urls)))