from typing import List, Tuple

from type_extractor import TypeExtractor
from number_extractor import extract_number
from date_extractor import extract_date


class Solution:

    def __init__(self):
        self.type_extractor = TypeExtractor()

    def train(self, train: List[Tuple[str, dict]]) -> None:
        self.type_extractor.train(train)

    def predict(self, test: List[str]) -> List[dict]:
        results = []
        pred_types = self.type_extractor.predict(test)
        for i, doc in enumerate(test):
            pred_number = extract_number(doc, pred_types[i])
            pred_date = extract_date(doc, pred_types[i])
            prediction = {"type": pred_types[i],
                          "date": pred_date,
                          "number": pred_number,
                          "authority": "",
                          "name": ""}
            results.append(prediction)
        return results
