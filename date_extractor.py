import re

month2number = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12'
}

date_reg_exprs = [
    re.compile(r'от (\d?\d) ([а-я]+) (\d\d\d\d)'),
    re.compile(r'(\d\d)\.(\d\d)\.(\d\d\d\d)'),
    re.compile(r'\n(\d?\d) ([а-я]+) (\d\d\d\d)')
]


def process_match(match):
    day = match[0] if len(match[0]) == 2 else '0' + match[0]
    month = month2number[match[1]] if match[1] in month2number else match[1]
    year = match[2]
    return day, month, year


def extract_date(doc, doc_type):
    matches = []
    variants = []
    doc = '\n' + doc.lower() + '\n'
    doc = re.sub(r'\n+', r'\n', doc)

    if doc_type == 'федеральный закон':
        match = re.search(r'\n(\d?\d) ([а-я]+) (\d\d\d\d) года\n', doc)
        if match:
            date = process_match((match.group(1), match.group(2), match.group(3)))
            return f'{date[0]}.{date[1]}.{date[2]}'

    if doc_type == 'приказ':
        match = re.search(r'приказ\n([^\n]*\n)?([^\n]*\n)?(от )?(\d?\d) ([а-я]+) (\d\d\d\d)', doc)
        if match:
            date = process_match((match.group(4), match.group(5), match.group(6)))
            return f'{date[0]}.{date[1]}.{date[2]}'
        match = re.search(r'приказ\n([^\n]*\n)?([^\n]*\n)?(от )?(\d\d\.\d\d\.\d\d\d\d)', doc)
        if match:
            return match.group(4)

    if doc_type == 'указ':
        match = re.search(r'указ\n([^\n]*\n)?([^\n]*\n)?([^\n]*\n)?(от )?(\d?\d) ([а-я]+) (\d\d\d\d)', doc)
        if match:
            date = process_match((match.group(5), match.group(6), match.group(7)))
            return f'{date[0]}.{date[1]}.{date[2]}'
        match = re.search(r'указ\n([^\n]*\n)?([^\n]*\n)?([^\n]*\n)?(от )?(\d\d\.\d\d\.\d\d\d\d)', doc)
        if match:
            return match.group(5)

    if doc_type == 'распоряжение':
        match = re.search(r'\n(\d\d\.\d\d\.\d\d\d\d)[^\n]*\n№ [\w\-/а-я]+\n', doc)
        if match:
            return match.group(1)

    if doc_type == 'постановление':
        match = re.search(
            r'постановление\n([^\n\d]*\n)?([^\n\d]*\n)?([^\n\d]*\n)?(от[_\- ]+?)?(\d?\d) ([а-я]+) (\d\d\d\d)', doc)
        if match:
            date = process_match((match.group(5), match.group(6), match.group(7)))
            return f'{date[0]}.{date[1]}.{date[2]}'
        match = re.search(r'постановление\n([^\n\d]*\n)?([^\n\d]*\n)?([^\n\d]*\n)?[а-я_\- ]*(\d\d\.\d\d\.\d\d\d\d)',
                          doc)
        if match:
            return match.group(4)

    if doc_type == 'закон':
        match = re.search(r'\n(\d\d\.\d\d\.\d\d\d\d)[^\n]*\n№ [\w\-/а-я]+\n', doc)
        if match:
            return match.group(1)
        match = re.search(r'\n(от )?(\d?\d) ([а-я]+) (\d\d\d\d)[^\n]*\n№ [\w\-/а-я]+\n', doc)
        if match:
            date = process_match((match.group(2), match.group(3), match.group(4)))
            return f'{date[0]}.{date[1]}.{date[2]}'

    for expr in date_reg_exprs:
        matches += expr.findall(doc)
    if matches:
        for match in matches:
            variants.append(process_match(match))
    else:
        matches = re.findall(r'(\d?\d) ([а-я]+) (\d\d\d\d)', doc)
        for match in matches:
            variants.append(process_match(match))

    date = variants[0] if variants else ''
    for variant in variants:
        if f'{variant[2]}.{variant[1]}.{variant[0]}' > f'{date[2]}.{date[1]}.{date[0]}':
            date = variant
    return f'{date[0]}.{date[1]}.{date[2]}' if date else date
