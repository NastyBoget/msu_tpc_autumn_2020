import re

PREPR_EXPR = re.compile(r'[^\wа-яА-Я\"\s.,;:№\-)(]')


def preprocess_doc(doc):
    doc = '\n' + doc.lower()
    doc = re.sub('_', ' ', doc)
    doc = re.sub(' +', ' ', doc)
    doc = re.sub(r'кои ', 'кой ', doc)
    return PREPR_EXPR.sub('', doc)


organizations = re.compile(r'правительств[оа]|министерство|администраци[яи]|управление|' 
                           'комитет|департамент|президента?|губернатора?|главы|'
                           'законодательное собрание|кабинет министров|областное собрание|'
                           'конституционный суд|конституционного суда|государственная дума|дума')


def ukaz_authority(doc):
    variants = []
    match = re.search(r'президента\s+российской\s+федерации', doc)
    if match:
        variants.append(('президент российской федерации', match.span()[0]))

    match = re.search(r'губернатора? ', doc)
    if match:
        index = match.span()[0]
        doc1 = doc[index:]
        authority = doc1.split('\n')[0]
        authority = 'губернатор ' + ' '.join(authority.split(' ')[1:])
        variants.append((authority, index))
    index = doc.find('главы')
    if index != -1:
        doc1 = doc[index:]
        authority = doc1.split('\n')[0]
        authority = 'глава ' + ' '.join(authority.split(' ')[1:])
        variants.append((authority, index))
    match = re.search(r'глава\s*\n', doc)
    if match:
        index = match.span()[0]
        doc1 = doc[index:]
        authority = 'глава ' + doc1.split('\n')[1]
        variants.append((authority, index))
    for author in ['глава ', 'губернатор\n']:
        index = doc.find(author)
        if index != -1:
            doc1 = doc[index:]
            authority = author + doc1.split('\n')[1]
            variants.append((authority, index))
    if variants:
        authority = variants[0][0]
        index = variants[0][1]
        for a, i in variants:
            if i < index:
                authority = a
                index = i
        return authority
    return ""


PRIKAZ_EXPR = re.compile(r'\n([^\n]*(управление|министерство|департамент|'
                         r'федеральная|служба|комитет|агентство)([^\n]+\n)*)\n')


def prikaz_authority(doc):
    match = PRIKAZ_EXPR.search(doc)
    if match:
        return match.group(1)
    return ""


ZAKON_EXPR = re.compile(
    r'принят[ \n]([^\n]*(государственн|совет|законодательн|собрание|'
    r'областн|дум|народн|курултай|президент)[^\n\d]*(\n[а-я\-\s]+\d\d)?)')
ZAKON_EXPR_2 = re.compile(r'\n([а-я\s]+)\s[^\s]*постановляет')
ZAKON_EXPR_3 = re.compile(r'\nзакон\n\n([а-я ]+)\n\n')

lemmatizer = {
    'законодательным': 'законодательное', 'областной': 'областная', 'думой': 'дума',
    'народным': 'народное', 'президентом': 'президент', 'государственным': 'государственный',
    'областное': 'областным', 'законодательной': 'законодательная',
    'собранием': 'собрание', 'советом': 'совет',
}


def zakon_authority(doc):
    if doc.startswith('\nкостромская областная дума'):
        return 'костромская областная дума'
    match = ZAKON_EXPR_2.search(doc)
    if match:
        return match.group().strip()
    match = ZAKON_EXPR_3.search(doc)
    if match:
        return 'законодательная дума ' + match.group(1).strip()

    match = ZAKON_EXPR.search(doc)
    if not match:
        if not match:
            return ""
    tokens = re.sub(r'[^а-я \-]', ' ', match.group(1)).split(' ')
    authority = ""
    for token in tokens:
        if token in lemmatizer:
            authority += lemmatizer[token] + ' '
        else:
            authority += token + ' '
    authority = re.sub(r'ой( [а-я\-]* ?дума)', r'ая\1', authority)
    return authority


POST_EXPR_1 = re.compile(r'(([а-я\s]+\n)?[^\n]+области)\n+постановление\n')
POST_EXPR_2 = re.compile(r'(правительство\n?[^\n]+)\n+постановление\n')
POST_EXPR_3 = re.compile(r'постановление[ \n]+губернатора[ \n]([а-я ]+)')
POST_EXPR_4 = re.compile(r'([^\n]+) постановляет')


def post_authority(doc):
    match = POST_EXPR_1.search(doc)
    if match:
        return match.group(1).strip()
    match = POST_EXPR_2.search(doc)
    if match:
        return match.group(1).strip()
    match = POST_EXPR_3.search(doc)
    if match:
        return 'губернатор ' + match.group(1).strip()
    match = POST_EXPR_4.search(doc)
    if match and len(match.group(1).split(' ')) > 2:
        authority = match.group(1).strip()
        authority = re.sub(r'(от )?\d.*', '', authority)
        return authority
    return ""


def extract_authority(doc, doc_type):
    if doc_type == 'федеральный закон':
        return 'Государственная Дума Федерального собрания Российской Федерации'
    doc = '\n' + doc.lower()
    doc = re.sub(r'[^\s]?при[нвп]ят', 'принят', doc)
#     doc = re.sub(r'я[^\s]+о-не[^\s]+го ', 'ямало-ненецкого', doc)
    if doc_type == 'указ':
        authority = ukaz_authority(doc)
        if authority:
            return authority
    elif doc_type == 'приказ':
        authority = prikaz_authority(doc)
        if authority:
            return authority
    elif doc_type == 'закон':
        authority = zakon_authority(doc)
        if authority:
            return authority
    elif doc_type == 'постановление':
        authority = post_authority(doc)
        if authority:
            return authority
    authority = ""
    matches = organizations.findall(doc)
    if matches:
        organization = matches[0]
        index = doc.find(organization)
        doc = doc[index:]
        authority = doc.split('\n')[0]
#             if len(authority.split(' ')) == 1:
        if authority == organization:
            authority += ' ' + doc.split('\n')[1]
        if authority.startswith('президента'):
            authority = re.sub('президента', 'президент', authority)
        if authority.startswith('губернатора'):
            authority = re.sub('губернатора', 'губернатор', authority)
        if authority.startswith('правительства'):
            authority = re.sub('правительства', 'правительство', authority)
        if authority.startswith('администрации'):
            authority = re.sub('администрации', 'администрация', authority)
        if authority.startswith('конституционного суда'):
            authority = re.sub('конституционного суда', 'конституционный суд', authority)
        authority = re.sub(r'(от )?\d.*', '', authority)
        return authority
    index = doc.find('принят ')
    if index != -1:
        doc = doc[index + 6:]
        authority = doc.split('\n')[0]
        authority = re.sub(r'(от )?\d.*', '', authority)

    return authority


NAME_EXPR = re.compile(r'(\nоб?\s[а-я]([^\n]+\n)+\n)')
UKAZ_EXPR = re.compile(r'(\nвопросы\s([^\n]+\n)+\n)')
POST_EXPR = re.compile(r'"о\s[^"]+"')
LAST_EXPR = re.compile(r'(об? ([^\n]+\n)+)\n')
POST2_EXPR = re.compile(r'(о внесении изменени[яй] [^\"]+)\"')


def extract_name(doc, doc_type):
    doc = preprocess_doc(doc)
    match = NAME_EXPR.search(doc)
    if match:
        name = match.group(0).strip()
        if doc.find('правительство пензенской области') != -1:
            match = POST2_EXPR.search(name)
            if match:
                return match.group(0).strip()
        return name
    if doc_type == 'указ':
        match = UKAZ_EXPR.search(doc)
        if match:
            return match.group(0).strip()
    match = POST_EXPR.search(doc)
    if match:
        return match.group()
    match = LAST_EXPR.search(doc)
    if match:
        return match.group(0).strip()
    return ""
