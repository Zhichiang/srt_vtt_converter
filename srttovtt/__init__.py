import re


def convert(file):
    count = 1
    content = ''
    ret_str = ['WEBVTT']

    for line in file:
        line = line.strip()

        if re.match("^\d+$", line):
            continue

        if re.match("^\d\d:\d\d:\d\d,\d\d\d\W-->\W\d\d:\d\d:\d\d,\d\d\d$", line):
            if content.strip() != "":
                ret_str.append(content.strip())
            content = line.replace(',', '.') + '\n'
            count += 1
            continue
        content += line + '\n'

    ret_str.append(content.strip())

    return '\n\n'.join(ret_str)


