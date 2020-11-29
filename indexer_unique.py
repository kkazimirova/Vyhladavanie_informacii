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
    # name = process_name(name)
    return name


def parse_alternative_name(line):
    splits = line.split(":")
    alternative_names = splits[1].strip()
    alternative_names_list = alternative_names.split(',')
    alternative_names_list = list(map(lambda x: x.strip(), alternative_names_list))
    return alternative_names_list


def make_dict_name_alternates(filename):
    file = open(filename, mode="r", encoding='utf8')
    lines = file.readlines()
    lines_gen = lines_generator(lines)

    records = {}

    while lines:
        try:
            name = next(lines_gen)
            # print(name)
            name_parsed = parse_name(name)
            # print(name_parsed)

            alternative_name = next(lines_gen)
            # print(alternative_name)
            alternative_name = parse_alternative_name(alternative_name)

            _ = next(lines_gen)


            if alternative_name[0]:
                if name_parsed in records:
                    pom = records[name_parsed]
                    records[name_parsed] = pom + alternative_name
                    # print(records[name_parsed])
                    # pass
                else:
                    records[name_parsed] = alternative_name
                    # print(records[name_parsed])

        except StopIteration:
            break


    file.close()
    return records


def make_dict_alternates_name(filename):
    file = open(filename, mode="r", encoding='utf8')
    lines = file.readlines()
    lines_gen = lines_generator(lines)

    records = {}

    while lines:
        try:
            name = next(lines_gen)
            # print(name)
            name_parsed = [parse_name(name)]
            # print(name_parsed)

            alternative_name = next(lines_gen)
            # print(alternative_name)
            alternative_name = parse_alternative_name(alternative_name)

            _ = next(lines_gen)
            if alternative_name[0]:
                for alt in alternative_name:
                    # print("alt: ", alt)
                    if alt in records:
                        pom = records[alt]
                        records[alt] = pom + name_parsed
                        # print("value ", records[alt], "key: ", alt)
                        # pass
                    else:
                        records[alt] = name_parsed
                        # print(records[alt])

        except StopIteration:
            break


    file.close()
    return records

def save_dict_name_alternate (dict, ):
    file = open("Outputs/uniq_name_alternate.txt", mode="w", encoding='utf8')

    for name, alternetive in dict.items():
        file.write("Name: " + name + '\n')
        file.write("Alternate: " + str(alternetive) + '\n')
        file.write("\n")

    file.close()



def save_dict_alternate_name (dict, ):
    file = open("Outputs/uniq_alternate_name.txt", mode="w", encoding='utf8')

    for alternetive, name in dict.items():
        file.write("Name: " + str(name) + '\n')
        file.write("Alternative: " + alternetive + '\n')
        file.write("\n")

    file.close()





if __name__ == '__main__':
    records_names_alternatives = make_dict_name_alternates(config.wikipedia_output)
    save_dict_name_alternate(records_names_alternatives)

    records_alternatives_names = make_dict_alternates_name(config.wikipedia_output)
    save_dict_alternate_name(records_alternatives_names)






