import bz2file
import re
import config


class RecordAlternate:
    def __init__(self, title_lower, title, alternatives=[]):
        self.title_lower = title_lower
        self.title = title
        self.alternates = alternatives

def open_files():
    wiki_bz_file = bz2file.open(config.wiki_file, mode="rt", encoding='utf8')
    output_file = open(config.parsed_names_and_alternats_file, mode="w", encoding='utf8')

    return wiki_bz_file, output_file

def close_files(wiki_file, output_file):
    wiki_file.close()
    output_file.close()


def parse_names_alternates(wiki_file, output_file):
    for line in iter(wiki_file.readline, ''):
        if is_infobox_start(line):
            name_infobox = None
            alternate_infobox = None

            for line2 in iter(wiki_file.readline, ''):
                name_temp = is_name(line2)
                is_oneliner, alternate_temp = is_list_oneliner(line2)

                if not is_oneliner:
                    is_list = is_list_more_lines(line2)
                    if is_list:
                        temp = ''
                        for line3 in iter(wiki_file.readline, ''):
                            end, item = list_item(line3)
                            temp = temp + ', ' + item
                            if end:
                                break
                        alternate_temp = temp
                    else:
                        alternate_temp = is_alternate(line2)

                if name_temp:
                    name_infobox = name_temp
                if alternate_temp:
                    alternate_infobox = alternate_temp

                if name_infobox and alternate_infobox:
                    name_infobox = parse_output(name_infobox)
                    alternate_infobox = parse_output(alternate_infobox)
                    output_file.write("name: " + name_infobox + "\nalternative name: " + alternate_infobox + "\n\n")
                    break
                if is_infobox_end(line2):
                    break

    return wiki_file, output_file


def parse_names_only(wiki_file, output_file):
    for line in iter(wiki_file.readline, ''):
        if is_infobox_start(line):
            name_infobox = None

            for line2 in iter(wiki_file.readline, ''):
                name_temp = is_name(line2)


                if name_temp:
                    name_infobox = name_temp

                if name_infobox:
                    name_infobox = parse_output(name_infobox)
                    output_file.write("name: " + name_infobox + "\n\n")
                    break
                if is_infobox_end(line2):
                    break

    return wiki_file, output_file


def is_infobox_start(line):
    found = re.search("^{{Infobox", line)
    return found


def is_infobox_end(line):
    found = re.search(r'^}}', line)
    return found


def is_name(line):
    found = re.search("^( *)\|( *)[N,n]ame", line)
    if found:
        splits = line.split("=")
        if len(splits) > 1:
            name = splits[1]
            name = parse_name(name)
        else:
            name = None
        return name
    return None


def is_list_oneliner(line):
    dictionary = ['other_name', 'alias', 'alternate_names', 'aka', 'alternate_name', 'altname', 'other_names', 'othernames']
    alternates = []
    is_list = False
    for word in dictionary:
        found = re.search(r"^\|( *)%s" %word, line)
        if found:
            splits = line.split("=", 1)
            if len(splits) > 1:
                alternate = splits[1]
                is_list = re.search(r"{{(ubl|hlist|unbulleted list).*}}", alternate)

                if is_list:
                    alternate = parse_alternate(alternate)
                    if alternate:
                        alternates = alternate.split("|")
                    else:
                        return is_list, ""
            break

    result = ', '.join(alternates[1:])

    if is_list is None:
        is_list = False
    return is_list, result


def is_list_more_lines(line):
    dictionary = ['other_name', 'alias', 'alternate_names', 'aka', 'alternate_name', 'altname', 'other_names', 'othernames']
    for word in dictionary:
        found = re.search(r"^\|( *)%s" %word, line)
        if found:
            splits = line.split("=", 1)
            if len(splits) > 1:
                alternate = splits[1]
                is_list = re.search(r"list(\||\}\}|\n)", alternate)
                if is_list:
                    # print("lala ", line)
                    return True
            else:
                return False
    return False


def list_item(line):
    ending_tag = re.search(r"{{Endplainlist}}", line)
    if ending_tag:
        list_end = True
        item = ''
        return list_end, item

    list_end = re.search(r"}}", line)
    item = parse_alternate(line)

    if item is None:
        item = ''

    return list_end, item


def is_alternate(line):
    dictionary = ['other_name', 'alias', 'alternate_names', 'aka', 'alternate_name', 'altname', 'other_names', 'othernames']

    for word in dictionary:
        found = re.search(r"^\|( *)%s" %word, line)
        if found:
            splits = line.split("=", 1)
            if len(splits) > 1:
                alternate = splits[1]
                alternate = parse_alternate(alternate)
            else:
                alternate = None

            return alternate
    return None


def parse_name(name):
    name = re.sub(r'\n', '', name)
    name = re.sub(r"&lt;br[\s]?.?&gt;", ", ", name)
    name = re.sub(r'&lt(.*?)&gt;', '', name)
    name = re.sub(r"&quot;", "\"", name)
    name = re.sub(r"&amp;", "&", name)
    name = re.sub(r"{{raise\|.* ?\|", "", name)
    name = re.sub(r"{{lang.*?\|.*?\|", "", name)
    name = re.sub(r"\[\[[\w\s\(\)]*\|", "", name)
    name = re.sub(r"\[\[|\]\]", "", name)
    name = re.sub(r"}}", "", name)
    name = re.sub(r"''+", "", name)
    name = re.sub(r"\|.*", "", name)

    if name.isspace():
        return None

    return name


def parse_alternate(alternate_line):
    alternate_line = re.sub(r"''+", "", alternate_line)
    alternate_line = re.sub(r"&amp;", "&", alternate_line)
    alternate_line = re.sub(r"&quot;", "\"", alternate_line)
    alternate_line = re.sub(r"&lt;((br[\s]?\/?)|(hr\/))&gt;", ", ", alternate_line)
    alternate_line = re.sub(r"{{citation(.*?)}}", "", alternate_line)
    alternate_line = re.sub(r"{{[Cc]ite (.*?)}}", "", alternate_line)
    alternate_line = re.sub(r"{{small\|", "", alternate_line)
    alternate_line = re.sub(r"\[http(s?):.* ?]", "", alternate_line)
    alternate_line = re.sub(r"&lt(.*?)&gt;", "", alternate_line)
    alternate_line = re.sub(r"{{lang.*?\|.*?\|", "", alternate_line)
    alternate_line = re.sub(r"{{lang.*?\|", "", alternate_line)
    alternate_line = re.sub(r"{{transl.*?\|.*?\|", "", alternate_line)
    alternate_line = re.sub(r"{{native name\|.*?\|", "", alternate_line)
    alternate_line = re.sub(r"{{[Pp]ad top italic\|", "", alternate_line)
    alternate_line = re.sub(r"{{okina", "", alternate_line)
    alternate_line = re.sub(r"{{longitem\|", "", alternate_line)
    alternate_line = re.sub(r"{{nowrap\|", "", alternate_line)
    alternate_line = re.sub(r"}}", "", alternate_line)
    alternate_line = re.sub(r"\[\[[\w\s\(\)]*\|", "", alternate_line)
    alternate_line = re.sub(r"\[\[|\]\]", "", alternate_line)
    alternate_line = re.sub(r"\n", "", alternate_line)
    alternate_line = re.sub(r"\*", "", alternate_line)
    alternate_line = re.sub(r"\s*\|\s+", "", alternate_line)

    if alternate_line.isspace():
        return None

    return alternate_line


def parse_output(output_line):
    output_line = re.sub(r"(^, *)|(^\s*)", "", output_line)
    output_line = re.sub(r";", ",", output_line)
    output_line = re.sub(r"\s*,\s*", ", ", output_line)

    return output_line


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
    alternative_names_list = alternative_names.split(',')
    alternative_names_list = list(map(lambda x: x.strip(), alternative_names_list))
    return alternative_names_list


def make_dict_name_alternates(filename):
    file = open(filename, mode="r", encoding='utf8')
    lines = file.readlines()
    lines_gen = lines_generator(lines)

    records = {}
    document_count = 0


    while lines:
        try:
            name = next(lines_gen)
            name_parsed = parse_name(name)
            alternative_name = next(lines_gen)
            alternative_name = parse_alternative_name(alternative_name)
            _ = next(lines_gen)

            if name_parsed in records:
                if alternative_name[0]:
                    stored_alt = records[name_parsed]
                    records[name_parsed] = stored_alt + alternative_name

            else:
                if alternative_name[0]:
                    records[name_parsed] = alternative_name
                else:
                    records[name_parsed] = []
            document_count += 1
        except StopIteration:
            break

    print("total count in name -> alternate dict:", document_count)
    file.close()
    return records


def make_dict_alternates_name(filename):
    file = open(filename, mode="r", encoding='utf8')
    lines = file.readlines()
    lines_gen = lines_generator(lines)

    records = {}
    document_count = 0
    while lines:
        try:
            name = next(lines_gen)
            name_parsed = [parse_name(name)]
            alternative_name = next(lines_gen)
            alternative_name = parse_alternative_name(alternative_name)

            _ = next(lines_gen)
            if alternative_name[0]:
                for alt in alternative_name:
                    if alt in records:
                        pom = records[alt]
                        records[alt] = pom + name_parsed
                    else:
                        records[alt] = name_parsed
            document_count += 1

        except StopIteration:
            break

    print("total parsed infoboxes:", document_count)

    file.close()
    return records


def save_dict_name_alternate (dict):
    file = open(config.uniq_alternatives_for_name, mode="w", encoding='utf8')

    for name, alternetive in dict.items():
        file.write("Name: " + name + '\n')
        file.write("Alternate: " + str(alternetive) + '\n')
        file.write("\n")

    file.close()


def save_dict_alternate_name(dict):
    file = open(config.uniq_names_for_alternative, mode="w", encoding='utf8')

    for alternative, name in dict.items():
        file.write("Name: " + str(name) + '\n')
        file.write("Alternative: " + alternative + '\n')
        file.write("\n")

    file.close()


if __name__ == '__main__':
    wiki_file, parsed_infoboxes_file = open_files()
    wiki_file, parsed_infoboxes_file = parse_names_alternates(wiki_file, parsed_infoboxes_file)
    wiki_file, parsed_infoboxes_file = parse_names_only(wiki_file, parsed_infoboxes_file)
    close_files(wiki_file, parsed_infoboxes_file)

    records_names_alternatives = make_dict_name_alternates(config.parsed_infoboxes_file)
    save_dict_name_alternate(records_names_alternatives)
    records_alternatives_names = make_dict_alternates_name(config.parsed_infoboxes_file)
    save_dict_alternate_name(records_alternatives_names)
