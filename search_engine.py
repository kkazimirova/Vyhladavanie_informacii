from datetime import datetime
import re
from more_itertools import strip

import config


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


def read_file():
    file = open(config.parsed_names_and_alternats_file, mode="r", encoding='utf8')
    lines = file.readlines()
    lines_gen = lines_generator(lines)

    memory = {}

    while lines:
        try:
            name = next(lines_gen)
            name = parse_name(name)

            alternative_name = next(lines_gen)
            alternative_name = parse_alternative_name(alternative_name)

            _ = next(lines_gen)

            # print(name, alternative_name, '\n')

            memory[name] = alternative_name

        except StopIteration:
            break

    file.close()

    return memory

def process_name(name):
    name = name.lower()
    name = re.sub(r'[^a-z]', '', name)
    return name


if __name__ == '__main__':
    mem = read_file()

    while True:
        print('Insert Wikipedia title: ')
        input_name = input()
        input_name = process_name(input_name)
        print(input_name)


        try:
            alternative = mem[input_name]
            print('\nAlternative names:')
            print(alternative)
            print('\n')

        except KeyError:
            print("\nNot found\n")


    print(mem)

--thomasandrewwilliamson