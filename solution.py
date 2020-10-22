from typing import List, Tuple

from type_extractor import TypeExtractor
from number_extractor import extract_number


class Solution:

    def __init__(self):
        self.type_extractor = TypeExtractor()

    def train(self, train: List[Tuple[str, dict]]) -> None:
        self.type_extractor.train(train)

    def predict(self, test: List[str]) -> List[dict]:
        results = []
        pred_types = self.type_extractor.predict(test)
        for i, doc in enumerate(test):
            pred_number = extract_number(doc)
            prediction = {"type": pred_types[i],
                          "date": "",
                          "number": pred_number,
                          "authority": "",
                          "name": ""}
            results.append(prediction)
        return results
