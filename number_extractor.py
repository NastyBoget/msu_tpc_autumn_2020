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
R = re.compile(r"распоряжение\n([^\n\d]*\n){0,3}[^\n\d]*\d?\d[ \.]([а-я]+|\d\d)[ \.]\d\d\d\d[^\n]*[\s№]([\wа-я\-/]+):?\n")
P = re.compile(r"постановление\s*\n([^\n\d]*\n){0,3}[^\n\d]*\d?\d[ \.]([а-я]+|\d\d)[ \.]\d\d\d\d[^\n]*([\s№]|№ .?)([\wа-я\-/]+).?\n")


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
        matches = re.findall(r"\n№\s?([\wа-я\-/]+)\s", doc)
        if matches:
            return matches[-1]

    if doc_type == "указ":
        matches = re.findall(r"\n№\s(\d+)\s", doc)
        if matches:
            return matches[-1]

    match = re.search(r"№\s?([\wа-я\-/]+)\s", doc)
    if match:
        return match.group(1)
    return ""
