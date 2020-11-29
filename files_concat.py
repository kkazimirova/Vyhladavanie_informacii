f = open("Outputs/toto.txt", mode="w", encoding='utf8')


with open("./Outputs/output_cela_wiki.txt", encoding='utf8') as f_alt:
    alt_lines = f_alt.readlines()
    for line in alt_lines:
        f.write(line)

with open("./Outputs/output_cela_wiki_names.txt", encoding='utf8') as f_names:
    names_lines = f_names.readlines()
    for line in names_lines:
        if line != "\n":
            f.write(line)
            f.write("alternative name:\n")
            f.write("\n")

f.close()

