import re

number_reg_exprs = [
    re.compile(r' № [\w\-/А-Яа-я]+ *'),
    re.compile(r'\n№ [\w\-/А-Яа-я]+\n*'),
    re.compile(r'№[\w\-/А-Яа-я]+')
]


def extract_number(doc):
    number = ''
    matches = []
    for expr in number_reg_exprs:
        matches += expr.findall(doc)
    if matches:
        return matches[0].strip()[1:].strip()  # убираем номер
    return number
