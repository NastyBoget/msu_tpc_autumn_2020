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

NUM_DATE_EXPR_1 = re.compile(r'(\d?\d) ([а-я]+) (\d\d\d\d)[^№\n]*\n*[^№\n]*\n*№[ _]*([\w\-а-я/]+)')
NUM_DATE_EXPR_2 = re.compile(r'(\d\d\.\d\d\.\d\d\d\d)[^№\n]*\n*[^№\n]*\n*№[ _]*([\w\-а-я/]+)')


def process_match(match):
    day = match[0] if len(match[0]) == 2 else '0' + match[0]
    month = month2number[match[1]] if match[1] in month2number else match[1]
    year = match[2]
    return f'{day}.{month}.{year}'


def extract_number(doc, doc_type, doc_date):
    doc = doc.lower()
    number = ""

    if doc_type == 'постановление':
        match = re.search(r'постановление\n([^\n\d]*\n)?([^\n\d]*\n)?([^\n\d]*\n)?'
                          '(от[_\- ]+?)?\d?\d [а-я]+ \d\d\d\d[^\n]*[ _]\$?&?([\w\-/а-я]+)\n', doc)
        if match:
            return re.sub('ппп', 'пп', re.sub('_', '', match.group(5)))
        match = re.search(r'постановление\n([^\n\d]*\n)?([^\n\d]*\n)?([^\n\d]*\n)?'
                          '[а-я_\- ]*\d\d\.\d\d\.\d\d\d\d[^\n]*[ _]\$?&?([\w\-/а-я]+)\n', doc)
        if match:
            return re.sub('ппп', 'пп', re.sub('_', '', match.group(4)))

    if doc_type == 'распоряжение':
        match = re.search(r'\n(от[_\- ]+?)?\d\d\.\d\d\.\d\d\d\d[^\n]*\n*(№|ме) *([\w\-/а-я]+).?\n', doc)
        if match:
            return re.sub('_', '', match.group(3))

    if doc_type == 'приказ':
        match = re.search(r'приказ\n[^\n№]*\n*[^\n№]*№ ([\w\-/а-я ]+)', doc)
        if match:
            number = re.sub('_', '', match.group(1))
            number = re.sub(' -', '', number)
            return number.strip().split(' ')[-1]

    matches = [match[0] + match[1] for match in NUM_DATE_EXPR_2.findall(doc)]
    matches += [process_match((match[0], match[1], match[2])) + match[3]
                for match in NUM_DATE_EXPR_1.findall(doc)]
    for match in matches:
        if match.startswith(doc_date):
            number = match[10:]
            break

    if doc_type == 'закон':
        if number:
            number = re.sub(r'([^\-]*-[ко]з).*', r'\1', number)

    if not number and doc_type == 'приказ':
        matches = re.findall(r'(\d?\d [а-я]+ \d\d\d\d|\d\d\.\d\d\.\d\d\d\d)([^\n]+)\n', doc)
        if matches:
            number = re.sub('_', '', matches[0][1])
            number = re.sub(' -', '', number)
            return number.strip().split(' ')[-1]

    if not number and (doc_type == 'распоряжение' or doc_type == 'приказ'):
        match = re.search(r'распоряжение\n([^\n\d]*\n)?([^\n\d]*\n)?[^\n]+[ _]([\w\-/а-я]+)\n', doc)
        if match:
            return match.group(3)
        matches = re.findall(r'№ *([\w\-/а-я]+)', doc)
        number = matches[0] if matches else ""

    if (doc_type == 'закон' or doc_type == 'постановление') and not number:
        matches = re.findall(r'№ *([\w\-/а-я]+)', doc)
        number = matches[-1] if matches else ""

    if not number and (doc_type == 'указ'):
        match = re.search(r'№[^\n\d]*([\w\-/а-я]+)\n', doc)
        if match:
            return match.group(1)

    return re.sub('_', '', number)
