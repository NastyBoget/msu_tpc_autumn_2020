from sklearn.ensemble import GradientBoostingClassifier
import re
import numpy as np

from typing import List, Tuple

type_reg_exprs = [
    re.compile(r'[Ф|ф]едеральный [З|з]акон'),
    re.compile(r'ФЕДЕРАЛЬНЫЙ ЗАКОН'),
    re.compile(r'[П|п]остановление'),
    re.compile(r'ПОСТАНОВЛЕНИЕ'),
    re.compile(r'[З|з]акон'),
    re.compile(r'ЗАКОН'),
    re.compile(r'[П|п]риказ'),
    re.compile(r'ПРИКАЗ'),
    re.compile(r'[Р|р]аспоряжение'),
    re.compile(r'РАСПОРЯЖЕНИЕ'),
    re.compile(r'[У|у]каз'),
    re.compile(r'УКАЗ')
]

number_reg_exprs = [
    re.compile(r' № [\w\-/А-Яа-я]+ *'),
    re.compile(r'\n№ [\w\-/А-Яа-я]+\n*'),
    re.compile(r'№[\w\-/А-Яа-я]+')
]

classes2num = {
    'федеральный закон': 0,
    'постановление': 1,
    'приказ': 2,
    'распоряжение': 3,
    'закон': 4,
    'указ': 5
}

num2classes = {
    0: 'федеральный закон',
    1: 'постановление',
    2: 'приказ',
    3: 'распоряжение',
    4: 'закон',
    5: 'указ'
}


def make_features(X: List[str]):
    """
    X - list of document contents
    returns numpy array with document features
    """
    features = []
    for doc in X:
        doc_features = np.array([len(expr.findall(doc)) for expr in type_reg_exprs])
        features.append(doc_features)
    return np.array(features)


def extract_number(doc):
    number = ''
    matches = []
    for expr in number_reg_exprs:
        matches += expr.findall(doc)
    if matches:
        return matches[0].strip()[1:].strip()  # убираем номер
    return number


class Solution:

    def __init__(self):
        self.clf = GradientBoostingClassifier()

    def train(self, train: List[Tuple[str, dict]]) -> None:
        docs = []
        y = []
        for doc_info in train:
            docs.append(doc_info[0])
            y.append(classes2num[doc_info[1]['type']])
        y = np.array(y)
        X = make_features(docs)
        self.clf.fit(X, y)

    def predict(self, test: List[str]) -> List[dict]:
        results = []
        for doc in test:
            X_test = make_features([doc])
            pred_type = num2classes[self.clf.predict(X_test)[0]]
            pred_number = extract_number(doc)
            prediction = {"type": pred_type,
                          "date": "",
                          "number": pred_number,
                          "authority": "",
                          "name": ""}
            results.append(prediction)
        return results
