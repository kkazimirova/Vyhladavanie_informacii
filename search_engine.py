import re

from whoosh.fields import Schema, TEXT, ID
from whoosh import index
import os.path
from whoosh.qparser import QueryParser

import config


class RecordAlternate:
    def __init__(self, title_lower, title, alternates=[]):
        self.title_lower = title_lower
        self.title = title
        self.alternates = alternates


def process_name(name):
    name = name.lower()
    return name


def get_indexes():
    dir_name = "index_name_alternatives"
    ix_name_alternates = index.open_dir(dir_name)

    dir_name = "index_alternative_names"
    ix_alternate_names = index.open_dir(dir_name)

    return ix_name_alternates, ix_alternate_names

def parse_array_string(string):
    string = string.replace(']', '').replace('[', '')
    string_after = re.sub('\"\'', '', string)
    string_after = re.sub('\'\"', '', string_after)

    return string_after


def print_result(key, values):
    if values != "''":
        print(key, '-->', values)
    else:
        print(key, '--> No alternatives found')


def search(index_name_alts, index_alt_names, input):
    with index_name_alts.searcher() as searcher:
        query = QueryParser("lower", index_name_alts.schema).parse(input)
        results = searcher.search_names(query)

        print("\nSEARCH ALTERNATIVE NAMES FOR INFOBOX NAME: \n")

        if len(results) > 5:
            title = results[0].get("title")
            alternates = parse_array_string(results[0].get("alternates"))
            print_result(title, alternates)

            for res in results[1:5]:
                print(res.get("title"))
            print("Too many matches (", len(results), ") insert name more precisely")
        else:
            if results:
                for r in results:
                    title = r.get("title")
                    alternates = parse_array_string(r.get("alternates"))
                    print_result(title, alternates)

            else:
                print("Not found in Infoboxes as name")

    with index_alt_names.searcher() as searcher:
        query = QueryParser("lower", index_alt_names.schema).parse(input)
        results = searcher.search_names(query)

        print("\n--------------------------------------------------------- \n")
        print("SEARCH INFOBOX NAMES FOR ALTERNATIVE NAME: \n")

        if len(results) > 5:
            for res in results[0:5]:
                alt = res.get("alternate")
                titles = parse_array_string(res.get("titles"))
                print_result(alt, titles)
            print("Too many matches (", len(results), ") insert alternative name more precisely")
        else:
            if results:
                for r in results:
                    alt = r.get("alternate")
                    titles = parse_array_string(r.get("titles"))
                    print_result(alt, titles)

            else:
                print("Not found in Infoboxes as alternative name")


if __name__ == '__main__':
    index_name_alts, index_alt_names = get_indexes()
    while True:
        print('\nInsert expression to search in Infoboxes: ')
        term = input()
        term = process_name(term)
        search(index_name_alts, index_alt_names, term)
        print("\n\n")
