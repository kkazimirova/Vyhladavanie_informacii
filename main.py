import bz2file
import re


def open_input_file():
    bz_file = bz2file.open("la.bz2", mode="rt", encoding='utf8')
    # print(bz_file.tell())
    return bz_file

def open_output_file():
    file = open("output.txt", mode="w", encoding='utf8')
    return file


def read_file(input_file, output_file, offset=0):
    # input_file.seek(offset)
    for line in iter(input_file.readline, ''):
        if (is_infobox_start(line)):
            # offset = input_file.tell()
            # parse_infobox(input_file, offset, output_file)
            name_infobox = None
            alternate_infobox = None

            for line2 in iter(input_file.readline, ''):
                name_temp = is_name(line2)
                alternate_temp = is_alternate(line2)
                if name_temp:
                    name_infobox = name_temp
                if alternate_temp:
                    alternate_infobox = alternate_temp

                if name_infobox and alternate_infobox:
                    print("name: " + name_infobox)
                    print("alternate: " + alternate_infobox)
                    output_file.write("name: " + name_infobox + "\nalternative name: " + alternate_infobox + "\n")
                    break
                if is_infobox_end(line2):
                    break

            # print()

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
    name = re.sub(r'&lt(.*?)&gt;', '', name)
    name = re.sub(r"'*", "", name)


    if name.isspace():
        return None

    return name

def parse_alternate(alternate_line):
    print(alternate_line)

    alternate_line = re.sub(r"'*", "", alternate_line)
    alternate_line = re.sub(r"&amp;", "&", alternate_line)
    alternate_line = re.sub(r"&quot;", "\"", alternate_line)
    alternate_line = re.sub(r"&lt;br&gt;", ", ", alternate_line)

    alternate_line = re.sub(r"{{citation(.*?)}}", "", alternate_line)
    alternate_line = re.sub(r"{{[Cc]ite (.*?)}}", "", alternate_line)

    alternate_line = re.sub(r"{{small\|", "", alternate_line)


    alternate_line = re.sub(r"&lt(.*?)&gt;", "", alternate_line)

    alternate_line = re.sub(r"{{lang\|.*?\|", "", alternate_line)
    alternate_line = re.sub(r"}}", "", alternate_line)

    alternate_line = re.sub(r"\[\[[\w\s\(\)]*\|", "", alternate_line)
    alternate_line = re.sub(r"\[\[|\]\]", "", alternate_line)



    print(alternate_line)

    if alternate_line.isspace():
        return None

    return alternate_line

# def parse_infobox(input_file, offset, output_file):
#
#     input_file.seek(offset)
#
#     name_infobox = None
#     alternate_infobox = None
#
#     for line in iter(input_file.readline, ''):
#         name_temp = is_name(line)
#         alternate_temp = is_alternate(line)
#         if name_temp:
#             name_infobox = name_temp
#         if alternate_temp:
#             alternate_infobox = alternate_temp
#
#         if name_infobox and alternate_infobox:
#             print("name: " + name_infobox)
#             print("alternate: " + alternate_infobox)
#             output_file.write("name: " + name_infobox + "   alternative name: " + alternate_infobox)
#             break
#         if is_infobox_end(line):
#             break



if __name__ == '__main__':

    input_file = open_input_file()
    output_file = open_output_file()
    read_file(input_file, output_file)

