import re


def convert(file):
    count = 0
    content = '0\n'
    ret_str = []

    for line in file:
        line = line.strip()
        line.replace(u'\ufeff', u'')

        if line.encode('utf-8').decode('utf-8-sig').strip().upper() == "WEBVTT":
            continue

        if re.match("^\d+$", line):
            continue

        if re.match("^\d\d:\d\d:\d\d\.\d\d\d\W-->\W\d\d:\d\d:\d\d\.\d\d\d$", line):
            if content.strip() != str(count):
                ret_str.append(content.strip())
            count += 1
            content = str(count) + '\n'
            content += line.replace('.', ',') + '\n'
            continue
        content += line + '\n'

    ret_str.append(content.strip())

    return '\n\n'.join(ret_str)


