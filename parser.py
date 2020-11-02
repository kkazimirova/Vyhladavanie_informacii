from datetime import datetime

import bz2file
import re


def open_input_file():
    bz_file = bz2file.open("enwiki-latest-pages-articles.xml.bz2", mode="rt", encoding='utf8')
    # bz_file = open('vstup', mode='rt', encoding='utf8')
    return bz_file

def open_output_file():
    file = open("output.txt", mode="w", encoding='utf8')
    return file


def read_file(input_file, output_file, offset=0):
    for line in iter(input_file.readline, ''):
        if (is_infobox_start(line)):
            name_infobox = None
            alternate_infobox = None

            for line2 in iter(input_file.readline, ''):
                name_temp = is_name(line2)
                # print(line2)
                is_oneliner, alternate_temp = is_list_oneliner(line2)
                # if is_oneliner != False:
                #     print(is_oneliner)
                if not is_oneliner:
                    is_list = is_list_more_lines(line2)
                    if is_list:
                        temp = ''
                        for line3 in iter(input_file.readline, ''):
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
                    # print("name: " + name_infobox)
                    # print("alternate: " + alternate_infobox)
                    name_infobox = parse_output(name_infobox)
                    alternate_infobox = parse_output(alternate_infobox)
                    output_file.write("name: " + name_infobox + "\nalternative name: " + alternate_infobox + "\n\n")
                    break
                if is_infobox_end(line2):
                    break

    input_file.close()
    output_file.close()

def is_infobox_start(line):
    found = re.search("^{{Infobox", line)
    return found

# todo fixnut koniec infoboxu
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
    # print(line)
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
                    # print("IS LISTTTT: ", line, '\n', alternates)
            break

    result = ', '.join(alternates[1:])

    # for i in range(1, len(alternates)):
    #     result.join(alternates[i])
    # print(is_list,result)

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
    # print(alternate_line)

    alternate_line = re.sub(r"''+", "", alternate_line)
    alternate_line = re.sub(r"&amp;", "&", alternate_line)
    alternate_line = re.sub(r"&quot;", "\"", alternate_line)
    alternate_line = re.sub(r"&lt;((br[\s]?\/?)|(hr\/))&gt;", ", ", alternate_line)

    alternate_line = re.sub(r"{{citation(.*?)}}", "", alternate_line)
    alternate_line = re.sub(r"{{[Cc]ite (.*?)}}", "", alternate_line)

    alternate_line = re.sub(r"{{small\|", "", alternate_line)


    alternate_line = re.sub(r"\[http(s?):.* ?]", "", alternate_line)



    alternate_line = re.sub(r"&lt(.*?)&gt;", "", alternate_line)

    # {{lang|es|Cordillera de los Andes|}}
    alternate_line = re.sub(r"{{lang.*?\|.*?\|", "", alternate_line)
    alternate_line = re.sub(r"{{lang.*?\|", "", alternate_line)


    alternate_line = re.sub(r"{{transl.*?\|.*?\|", "", alternate_line)

    # {{native name | fr | Colombie - Britannique
    alternate_line = re.sub(r"{{native name\|.*?\|", "", alternate_line)

    # |other_name             = {{Pad top italic|{{lang|ga|Contae Mhaigh Eo}}}}
    alternate_line = re.sub(r"{{[Pp]ad top italic\|", "", alternate_line)

    # |other_name = {{okina}}Īao Valley
    alternate_line = re.sub(r"{{okina", "", alternate_line)
    alternate_line = re.sub(r"{{longitem\|", "", alternate_line)
    alternate_line = re.sub(r"{{nowrap\|", "", alternate_line)



    alternate_line = re.sub(r"}}", "", alternate_line)

    # Américo Vespucio ([[Spanish language|Spanish]]), Americus Vespucius ([[Latin]]),
    alternate_line = re.sub(r"\[\[[\w\s\(\)]*\|", "", alternate_line)
    alternate_line = re.sub(r"\[\[|\]\]", "", alternate_line)


    alternate_line = re.sub(r"\n", "", alternate_line)
    alternate_line = re.sub(r"\*", "", alternate_line)
    alternate_line = re.sub(r"\s*\|\s+", "", alternate_line)


    # print(alternate_line)

    if alternate_line.isspace():
        return None

    return alternate_line


def parse_output(output_line):
    output_line = re.sub(r"(^, *)|(^\s*)", "", output_line)
    output_line = re.sub(r";", ",", output_line)
    output_line = re.sub(r"\s*,\s*", ", ", output_line)


    return output_line




if __name__ == '__main__':
    print(datetime.now())

    input_file = open_input_file()
    output_file = open_output_file()
    read_file(input_file, output_file)
    print(datetime.now())

# alternative name:  Rock n roll junkie
# name:  Italian Greyhound
# alternative name:  {{ubl|FCI: Italian Sighthound| Italian: Piccolo levriero Italiano|italic=no
# name:  Manitoba
# alternative name:  {{native name|cr|Manitou-wapow, {{native name|oj|Manidoobaa