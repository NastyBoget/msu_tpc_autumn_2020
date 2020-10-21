from typing import List, Tuple


class Solution:

    def __init__(self):
        pass

    def train(self, train: List[Tuple[str, dict]]) -> None:
        # fit your models here
        pass

    def predict(self, test: List[str]) -> List[dict]:
        # Do some predictions here and return results
        # Let's return empty result in proper format
        results = []
        for _ in test:
            prediction = {"type": "",
                          "date": "",
                          "number": "",
                          "authority": "",
                          "name": ""}
            results.append(prediction)
        return results
