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


def lines_generator(lines):
    for line in lines:
        yield line


def parse_name(line):
    splits = line.split(":")
    name = splits[1].strip()
    name = process_name(name)
    return name


def parse_alternative_name(line):
    splits = line.split(":")
    alternative_names = splits[1].strip()
    alternative_names_list = alternative_names.split(',')
    alternative_names_list = list(map(lambda x: x.strip(), alternative_names_list))
    return alternative_names_list


def read_file_alternates(filename):
    file = open(filename, mode="r", encoding='utf8')
    lines = file.readlines()
    lines_gen = lines_generator(lines)

    records = []

    while lines:
        try:
            name = next(lines_gen)
            name_parsed = parse_name(name)

            alternative_name = next(lines_gen)
            alternative_name = parse_alternative_name(alternative_name)

            _ = next(lines_gen)

            record = RecordAlternate(name_parsed, name, alternative_name)
            records.append(record)

        except StopIteration:
            break

    file.close()
    return records


def read_file_make_dict(filename, dict):
    file = open(filename, mode="r", encoding='utf8')
    lines = file.readlines()
    lines_gen = lines_generator(lines)

    records = []

    while lines:
        try:
            name = next(lines_gen)
            name_parsed = parse_name(name)

            alternative_name = next(lines_gen)
            alternative_name = parse_alternative_name(alternative_name)

            _ = next(lines_gen)


        except StopIteration:
            break

    file.close()
    return records


def process_name(name):
    name = name.lower()
    # name = re.sub(r'[^a-z]', '', name)
    return name


def create_index_alternates(records):
    dir_name = "indexdirrrr"
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

        schema = Schema(lower=TEXT(stored=True), title=TEXT(stored=True), alternates=TEXT(stored=True))

        ix = index.create_in(dir_name, schema)

        writer = ix.writer()
        for record in records:
            writer.add_document(lower=u"%s" % record.title_lower, title=u"%s" % record.title, alternates=u"%s" % record.alternates)

        writer.commit()

    else:
        ix = index.open_dir(dir_name)

    return ix


def search(index_alternates, term):
    with index_alternates.searcher() as searcher:
        query = QueryParser("lower", index_alternates.schema).parse(term)
        # results = searcher.search(query, terms=True)
        results = searcher.search(query)


        if len(results) > 15:
            for res in results[0:5]:
                print(res.get("title"))
            print("too many matches - ", len(results))
        else:
            if results:
                for r in results:
                    title = r.get("title")
                    alternate = r.get("alternates")

                    if alternate != "alternative name:\n":
                        print(title, alternate, "\n")
                    else:
                        print(title, "No alternative name found\n")
                    # if results.has_matched_terms():
                    #     print("result marched terms   ", results.matched_terms())
            else:
                print("Not found")




if __name__ == '__main__':
    tento_dict = {}
    records_alternates = read_file_alternates(config.wikipedia_output)

    index_alternates = create_index_alternates(records_alternates)

    while True:
        print('\nInsert Wikipedia title: ')
        input_name = input()
        input_name = process_name(input_name)
        search(index_alternates, input_name)

# nickname

# ukazka aj aj Harold Rothman, richard keith