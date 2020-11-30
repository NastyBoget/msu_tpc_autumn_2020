import re
import numpy as np

subs = [
    (re.compile(r"[. ]*\b[пПНИ]?[Оо]?[СЗз][Г]?[Тт][АВ]Ц?[НВ]?[О.Я]?[БВ][АЛП]"
                r"[ЕР][НЦИ]И[ЕКВ]{0,3}\b|^А?Н?О?В?ЛЕНИЕ\b|ПОСТАНОВ(?:Л\b|:)"), "ПОСТАНОВЛЕНИЕ"),
    (re.compile(r"\b[ПНИ]{1,2} ?Р ?[И&] ?К ?А ?З?|\bПР и ?[зЗ3]"), "ПРИКАЗ"),
    (re.compile(r"[У'`] ?К ?А ?[З:]"), "УКАЗ"),
    (re.compile(r"^У\nГУБЕРНАТОРА", re.M), "УКАЗ\nГУБЕРНАТОРА"),
    (re.compile(r"З?АКОН?\b"), "ЗАКОН"),
    (re.compile(r"о? ?Р?АС[ПН]ОРЯЖЕНИЕ\b"), "РАСПОРЯЖЕНИЕ"),
]


def preprocess(doc):
    doc = '\n' + doc.lower()
    for temptate, substitute in subs:
        doc = re.sub(temptate, substitute, doc)
    return doc


exprs = ['закон\s|федеральный закон', 'приказ|истрировано', 'указ', 'распоряжение', 'постановление']


def find_best_match(types, doc):
    # matches: закон приказ указ распоряжение постановление
    ids = np.where(types)[0]
    expr = ""
    for i in ids:
        expr = f"{expr}|{exprs[i]}"
    if expr:
        expr = expr[1:]
    else:
        return 'закон'
    expr = re.compile(expr)

    matches = expr.findall(doc)
    if matches[0].strip() in ['закон', 'федеральный закон', 'указ', 'распоряжение', 'постановление']:
        return matches[0].strip()
    else:
        return 'приказ'


type_reg_exprs = [
    re.compile(r'закон|федеральный закон'),
    re.compile(r'приказ|истрировано'),
    re.compile(r'указ'),
    re.compile(r'распоряжение'),
    re.compile(r'постановление')
]


def extract_type(doc):
    doc = preprocess(doc)
    if re.search(r'костром[а-я]+ областная дума', doc) or re.search(r'о законе костромско[йи] области', doc):
        return 'закон'
    matches = np.array([expr.search(doc) for expr in type_reg_exprs])
    return find_best_match(matches, doc)
