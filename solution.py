from typing import List, Tuple

from type_extractor import extract_type
from number_extractor import extract_number
from date_extractor import extract_date
from authority_name_extractor import extract_name, extract_authority


class Solution:

    def __init__(self):
        pass

    def train(self, train: List[Tuple[str, dict]]) -> None:
        pass

    def predict(self, test: List[str]) -> List[dict]:
        results = []
        for doc in test:
            pred_type = extract_type(doc)
            pred_date = extract_date(doc, pred_type)
            pred_number = extract_number(doc, pred_type, pred_date)
            pred_name = extract_name(doc, pred_type)
            pred_authority = extract_authority(doc, pred_type)
            prediction = {"type": pred_type,
                          "date": pred_date,
                          "number": pred_number,
                          "authority": pred_authority,
                          "name": pred_name}
            results.append(prediction)
        return results
