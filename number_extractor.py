import re

date_reg_exprs = [
    re.compile(r'от \d?\d [А-Яа-я]+ \d\d\d\d[^\n]+'),
    re.compile(r'\d\d\.\d\d\.\d\d\d\d[^\n]+'),
    re.compile(r'\n\d?\d [А-Яа-я]+ \d\d\d\d[^\n]+')
]

date_num_reg_exprs = [
    re.compile(r'от \d?\d [А-Яа-я]+ \d\d\d\d[^\n№]+№[^\n№]+'),
    re.compile(r'\d\d\.\d\d\.\d\d\d\d[^\n№]+№[^\n№]+'),
    re.compile(r'\n\d?\d [А-Яа-я]+ \d\d\d\d[^\n№]+№[^\n№]+')
]

number_reg_exprs = [
    re.compile(r' *№°?[_ ]+([\w\-/А-Яа-я]+)[_ ]*'),
    re.compile(r'\n№°?[_ ]+([\w\-/А-Яа-я]+)\n*'),
    re.compile(r'№°?([\w\-/А-Яа-я]+)')
]


def extract_number(doc, doc_type):
    doc = doc.lower()
    if doc_type in ['постановление', 'распоряжение', 'приказ']:
        prev_match = None
        for expr in date_num_reg_exprs:
            match = expr.search(doc)
            if match and prev_match and prev_match[1] > match.span()[0]:
                prev_match = (match.group(), match.span()[0])
        if prev_match:
            doc = prev_match[0]
    matches = []
    for expr in number_reg_exprs:
        matches += list(map(lambda x: x.group(1), list(expr.finditer(doc))))
    if matches:
        if doc_type in ['постановление', 'распоряжение', 'приказ']:
            return matches[0]
        return matches[-1]
    else:
        for expr in date_reg_exprs:
            match = expr.search(doc)
            if match:
                matches = match.group()
                break
        if matches:
            return matches.strip().split(' ')[-1]
    return ''

