import re

organizations = ['правительство', 'губернатор', 'администрация', 'президента']


def extract_authority(doc):
    doc = doc.lower()
    authority = ""
    for organization in organizations:
        index = doc.find(organization)
        if index != -1:
            doc = doc[index:]
            authority = doc.split('\n')[0]
            if authority.startswith('президента'):
                authority = re.sub('президента', 'президент', authority)
            return authority
    index = doc.find('принят')
    if index != -1:
        doc = doc[index + 6:]
        authority = doc.split('\n')[0]
        authority = re.sub(r'\d.*', '', authority)
    return authority


def extract_name(doc):
    doc = doc.lower()
    name = re.search(r'\n((о|об) ([^\n]+\n)+)\n', doc)
    if name:
        return name.group(1)
    else:
        return ""
