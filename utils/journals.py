"""
This module loads the journal settings from /static/journals/journals.xml and does also schema validation
"""
from json import load as json_load
from importlib import import_module
from os import path
from utils.settings import APP_JOURNALS
import logging
logger = logging.getLogger(__name__)

def make_dict(path):
    journals_dict = {}

    with open(path) as json_file:
        journals = json_load(json_file)

        for journal in journals:
            journal_dict = {}
            
            for k, v in journal.items():
                if k in ("display", "baseLink", "section"):
                    # Copy these just as they are needed
                    journal_dict[k] = v
                elif k in ("crawler", "indexer"):
                    # Have to turn these into actual functions
                    mod_name, fun_name = v.split(".", 2)
                    mod = import_module(f"{k.lower()}s.{mod_name}")
                    fun = getattr(mod, fun_name)
                    journal_dict[k] = fun
            
            # Take the collection name as key
            journals_dict[journal["coll"]] = journal_dict
    return journals_dict

    """
    journals_dict = {}
    for journal_tag in ET.parse(path).getroot():
        journal_dict = {}
        for elem in journal_tag:
            tag = elem.tag
            if tag in ("Display", "BaseLink"): # just copy into the dict
                journal_dict[tag] = elem.text
            elif tag in ("Crawler", "Indexer"): # has to be turned into a function
                mod_name, fun_name = elem.text.split(".", 2)
                mod = import_module(f"{tag.lower()}s.{mod_name}")
                fun = getattr(mod, fun_name)
                journal_dict[tag] = fun
            elif tag == "Sections": # generate a list with the <Section> tags
                journal_dict[tag] = [section_tag.text for section_tag in elem]
        journals_dict[journal_tag.attrib["coll"]] = journal_dict
    return journals_dict
    """

json_path = path.join(APP_JOURNALS, "journals.json")
JOURNALS = make_dict(json_path)
