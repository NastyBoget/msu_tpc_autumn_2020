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
    re.compile(r'\n(\d?\d) ([а-я]+) (\d\d\d\d)'),
    re.compile(r'(\d\d)\.(\d\d)\.(\d\d\d\d)')
]


F_Z = re.compile(r'\n(\d?\d) ([а-я]+) (\d\d\d\d) года\n')
Z = re.compile(r'\n(от )?(\d?\d)[ \.]([а-я]+|\d\d)[ \.](\d\d\d\d)')
R = re.compile(r'\n(\d\d\.\d\d\.\d\d\d\d)[^\n]*\n№ [\w\-/а-я]+\n')
P = re.compile(r'постановление\n([^\n\d]*\n)?([^\n\d]*\n)?([^\n\d]*\n)?(от[_\- ]+?)?(\d?\d)[ \.]([а-я]+|\d\d)[ \.](\d\d\d\d)')
PRIKAZ = re.compile(r'приказ\n([^\n]*\n)?([^\n]*\n)?(от )?(\d?\d)[ \.]([а-я]+|\d\d)[ \.](\d\d\d\d)')
U = re.compile(r'указ\n([^\n]*\n)?([^\n]*\n)?([^\n]*\n)?(от )?(\d?\d)[ \.]([а-я]+|\d\d)[ \.](\d\d\d\d)')


def doc_preprocess(doc):
    doc = '\n' + doc.lower() + '\n'
    doc = re.sub(r"[_о](\d?\d [а-я]+ \d\d\d\d)", r"\1", doc)
    doc = re.sub(r"_(\d?\d\.\d\d\.\d\d\d\d)", r"\1", doc)
    doc = re.sub(r"\n+", "\n", doc)
    return doc


def process_match(match):
    day = match[0] if len(match[0]) == 2 else '0' + match[0]
    month = month2number[match[1]] if match[1] in month2number else match[1]
    year = match[2]
    return f"{day}.{month}.{year}"


def reverse_date(date):
    if len(date) == 10:
        return f"{date[6:]}.{date[3:5]}.{date[:2]}"
    return date


def find_max_date(variants, start=0):
    date = process_match(variants[0][start:]) if variants else ''
    for variant in variants:
        processed_variant = process_match(variant[start:])
        if reverse_date(processed_variant) > reverse_date(date):
            date = processed_variant
    return date


def extract_date(doc, doc_type):
    doc = doc_preprocess(doc)
    if doc_type == "федеральный закон":
        match = F_Z.search(doc)
        if match:
            return process_match((match.group(1), match.group(2), match.group(3)))

    if doc_type == 'распоряжение':
        match = R.search(doc)
        if match:
            return match.group(1)

    if doc_type == 'закон':
        matches = Z.findall(doc)
        if matches:
            date = find_max_date(matches, start=1)
            return date

    if doc_type == 'постановление':
        doc = re.sub(r"[пнл]оста[нв]ов[пнл]е[нпл]и[ек]", r"постановление", doc)
        match = P.search(doc)
        if match:
            return process_match((match.group(5), match.group(6), match.group(7)))

    if doc_type == 'приказ':
        match = PRIKAZ.search(doc)
        if match:
            return process_match((match.group(4), match.group(5), match.group(6)))

    if doc_type == 'указ' and not doc.find('о внесении изменений') != -1:
        match = U.search(doc)
        if match:
            return process_match((match.group(5), match.group(6), match.group(7)))

    matches = []
    for reg_expr in date_reg_exprs:
        matches += reg_expr.findall(doc)
    if matches:
        if doc_type == 'постановление' and re.search(r"\\сессии\\", doc):
            matches = matches[:-1]
        date = find_max_date(matches)
        return date
    matches = re.findall(r'(\d?\d) ([а-я]+) (\d\d\d\d)', doc)
    if matches:
        return find_max_date(matches)
    return ""
