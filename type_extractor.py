import re
import numpy as np


def preprocess(doc):
    doc = '\n' + doc.lower()
    doc = re.sub(r'[нп]рика[з3]', 'приказ', doc)
    doc = re.sub('ука3', 'указ', doc)
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
        return expr
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
    if re.search('костромская областная дума', doc):
        return 'закон'
    matches = np.array([expr.search(doc) for expr in type_reg_exprs])
    return find_best_match(matches, doc)
