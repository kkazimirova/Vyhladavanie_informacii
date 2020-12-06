from whoosh.fields import Schema, TEXT, ID
from whoosh import index
import os.path
from whoosh.qparser import QueryParser

import config


class RecordAlternativesForName:
    def __init__(self, title_lower, title, alternates=[]):
        self.title_lower = title_lower
        self.title = title
        self.alternates = alternates


class RecordNamesForAlternative:
    def __init__(self, alternate_lower, alternate, titles=[]):
        self.alternate_lower = alternate_lower
        self.alternate = alternate
        self.titles = titles


def lines_generator(lines):
    for line in lines:
        yield line


def parse_name(line):
    splits = line.split(":")
    name = splits[1].strip()
    return name


def parse_alternative_name(line):
    splits = line.split(":")
    alternative_names = splits[1].strip()
    alternative_names = alternative_names.replace(']', '').replace('[', '')

    alternative_names_list = alternative_names.split(',')
    alternative_names_list = list(map(lambda x: x.strip(), alternative_names_list))
    return alternative_names_list


def read_file_alternatives_for_name(filename):
    file = open(filename, mode="r", encoding='utf8')
    lines = file.readlines()
    lines_gen = lines_generator(lines)

    records = []

    while lines:
        try:
            name = next(lines_gen)
            name = parse_name(name)
            name_parsed = name.lower()
            alternative_name = next(lines_gen)
            alternative_name = parse_alternative_name(alternative_name)
            _ = next(lines_gen)

            record = RecordAlternativesForName(name_parsed, name, alternative_name)
            records.append(record)

        except StopIteration:
            break

    file.close()
    return records


def process_name(name):
    name = name.lower()
    return name


def create_index_alternatives_for_name(records):
    dir_name = "index_name_alternatives"
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
        results = searcher.search_names(query)


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

            else:
                print("Not found")


def parse_alternate(line):
    splits = line.split(":")
    alternate = splits[1].strip()
    return alternate


def parse_titles(line):
    splits = line.split(":")
    titles = splits[1].strip()
    titles = titles.replace(']', '').replace('[', '')

    titles_list = titles.split(',')
    titles_list = list(map(lambda x: x.strip(), titles_list))
    return titles_list


def read_file_names_for_alternative(filename):
    file = open(filename, mode="r", encoding='utf8')
    lines = file.readlines()
    lines_gen = lines_generator(lines)

    records = []

    while lines:
        try:
            names = next(lines_gen)
            names = parse_titles(names)
            alternate = next(lines_gen)
            alternate = parse_alternate(alternate)
            alt_parsed = alternate.lower()
            _ = next(lines_gen)

            record = RecordAlternativesForName(alt_parsed, alternate, names)
            records.append(record)

        except StopIteration:
            break
    file.close()
    return records


def process_alternates(alt):
    alt = alt.lower()
    return alt


def create_index_names_for_alternative(records):
    dir_name = config.index_names_for_alternative
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        schema = Schema(lower=TEXT(stored=True), alternate=TEXT(stored=True), titles=TEXT(stored=True))
        ix = index.create_in(dir_name, schema)

        writer = ix.writer()
        for record in records:
            writer.add_document(lower=u"%s" % record.alternate_lower, alternate=u"%s" % record.alternate, titles=u"%s" % record.titles)

        writer.commit()

    else:
        ix = index.open_dir(dir_name)

    return ix


def search_names(index_alternates, term):
    with index_alternates.searcher() as searcher:
        query = QueryParser("lower", index_alternates.schema).parse(term)
        # results = searcher.search(query, terms=True)
        results = searcher.search_names(query)


        if len(results) > 15:
            for res in results[0:5]:
                print(res.get("alternate"))
            print("too many matches - ", len(results))
        else:
            if results:
                for r in results:
                    title = r.get("alternate")
                    alternate = r.get("titles")

                    if alternate != "alternative name:\n":
                        print(title, alternate, "\n")
                    else:
                        print(title, "No alternative name found\n")
            else:
                print("Not found")


if __name__ == '__main__':
    records = read_file_names_for_alternative(config.uniq_names_for_alternative)
    index_alternatives_for_name = create_index_alternatives_for_name(records)

    records = read_file_alternatives_for_name(config.uniq_alternatives_for_name)
    index_names_for_alternatives = create_index_names_for_alternative(records)

