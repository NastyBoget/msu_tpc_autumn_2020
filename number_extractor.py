import re

PREPR_EXPR = re.compile(r'[^\wа-яА-Я\s\.,;:№\-/]')


def doc_preprocess(doc):
    doc = '\n' + doc.lower() + '\n'
    doc = re.sub("ппп", "пп", doc)
    doc = re.sub("- ", "", doc)
    doc = re.sub(" -", "", doc)
    doc = re.sub(r"[пнл]оста[нв]ов[пнл]е[нпл]и[ек]", r"постановление", doc)
    doc = re.sub(r"_+", "", doc)
    return PREPR_EXPR.sub('', doc)


F_Z = re.compile(r"\n№ ?([\wа-я\-/]+)\s")
Z = re.compile(r"\s№\s?([\wа-я\-/]+)\s")
R = re.compile(r"распоряжение\n([^\n\d]*\n){0,3}[^\n\d]*\d?\d[ \.]([а-я]+|\d\d)"
               r"[ \.]\d\d\d\d[^\n]*[\s№]([\wа-я\-/]+):?\n")
P = re.compile(r"постановление\s*\n([^\n\d]*\n){0,3}[^\n\d]*\d?\d[ \.]"
               r"([а-я]+|\d\d)[ \.]\d\d\d\d[^\n]*([\s№]|№ .?)([\wа-я\-/]+).?\n")

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

NUM_DATE_EXPR_1 = re.compile(r'(\d?\d) ([а-я]+) (\d\d\d\d)[^№\n]*\n*[^№\n]*\n*№[ _]*([\w\-а-я/]+)')
NUM_DATE_EXPR_2 = re.compile(r'(\d\d\.\d\d\.\d\d\d\d)[^№\n]*\n*[^№\n]*\n*№[ _]*([\w\-а-я/]+)')


def process_match(match):
    day = match[0] if len(match[0]) == 2 else '0' + match[0]
    month = month2number[match[1]] if match[1] in month2number else match[1]
    year = match[2]
    return f'{day}.{month}.{year}'


def extract_number(doc, doc_type, doc_date):
    doc = doc_preprocess(doc)

    if doc_type == "распоряжение":
        match = R.search(doc)
        if match:
            number = match.group(3)
            if re.search(r"\d", number):
                return number

    if doc_type == "федеральный закон" or doc_type == "распоряжение":
        matches = F_Z.findall(doc)
        if matches:
            return matches[-1]

    if doc_type == "закон":
        if doc.find('-кз') != -1 or doc.find('-оз') != -1 or doc.find('-рз') != -1:
            matches = re.findall("(\d+\-[кор]з)", doc)
            if matches:
                return matches[-1]
        matches = Z.findall(doc)
        if matches:
            return matches[-1]

    if doc_type == "постановление":
        match = P.search(doc)
        if match:
            number = match.group(4)
            if re.search(r'\b2\d\d\d', number):
                number = number[1:]
            if re.search(r"\d", number):
                return number
        doc1 = '\n'.join(doc.split('\n')[:15] + doc.split('\n')[-10:])
        matches = re.findall(r"\n№\s?([\wа-я\-/]+)\s", doc1)
        if matches:
            return matches[-1]

    matches = [match[0] + match[1] for match in NUM_DATE_EXPR_2.findall(doc)]
    matches += [process_match((match[0], match[1], match[2])) + match[3]
                for match in NUM_DATE_EXPR_1.findall(doc)]
    for match in matches:
        if match.startswith(doc_date):
            number = match[10:]
            return number

    if doc_type == "указ":
        matches = re.findall(r"\n№\s(\d+)\s", doc)
        if matches:
            return matches[-1]

    match = re.search(r"№\s?([\wа-я\-/]+)\s", doc)
    if match:
        return match.group(1)
    return ""
