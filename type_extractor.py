import re
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
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


class TypeExtractor:
    def __init__(self):
        self.clf = GradientBoostingClassifier()

    @staticmethod
    def make_features(X: List[str]):
        features = []
        for doc in X:
            doc_features = np.array([len(expr.findall(doc)) for expr in type_reg_exprs])
            features.append(doc_features)
        return np.array(features)

    def train(self, train: List[Tuple[str, dict]]):
        docs = []
        y = []
        for doc_info in train:
            docs.append(doc_info[0])
            y.append(classes2num[doc_info[1]['type']])
        y = np.array(y)
        X = self.make_features(docs)
        self.clf.fit(X, y)

    def predict(self, test: List[str]) -> List[str]:
        X_test = self.make_features(test)
        pred_type = [num2classes[i] for i in self.clf.predict(X_test)]
        return pred_type
