#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List, Set
import logging
logger = logging.getLogger(__name__)


def collect_links(node, filter=None) -> Set[str]:
    links = set()
    a_tags = node.find_all("a")
    if a_tags:
        for link in node.find_all("a"):
            href = link.get("href")
            if href and "javascript" not in href:
                if not filter or (filter and filter(href)):
                    links.add(href)
    return links


def story_link_filter(href):
    return "/story/" in href and "#talkback" not in href


def crawl(base_link, sec_soup) -> List[str]:
    story_urls = set()
    story_urls = collect_links(sec_soup, story_link_filter)
    story_urls = {base_link + url for url in story_urls}
    return list(story_urls)
