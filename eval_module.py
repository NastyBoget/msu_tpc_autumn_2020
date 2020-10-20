from typing import List
from statistics import mean
from sklearn.metrics import f1_score, accuracy_score
import re
from difflib import SequenceMatcher


def subtasks_improves(result: dict) -> int:
    BASELINE_SCORES = {
        'date_accuracy': 0.7996941896,
        'number_accuracy': 0.7262996942,
        'type_f1_score': 0.569159562,
        'name_jaccard': 0.7030790994,
        'authority_jaccard': 0.6447061931,
        'delta': 0.00001
    }
    subtasks_improves = int(len([metric for metric, value in result.items()
                             if BASELINE_SCORES[metric] + BASELINE_SCORES["delta"] < value]))
    return subtasks_improves    


def preprocess(text):
    text = text.lower()
    text = text.replace('\n', ' ')
    text = re.sub(" +", " ", text)
    return text


def string_jaccard_metric(gold_names, pred_names):
    scores = []
    for gold, pred in zip(gold_names, pred_names):
        if len(pred) == 0:
            scores.append(0)
            continue
        gold = gold.lower()
        pred = pred.lower()
        match = SequenceMatcher(None, gold, pred).find_longest_match(0, len(gold), 0, len(pred))

        gold_start_offset = match.a
        gold_end_offset = len(gold) - match.a - match.size
        pred_start_offset = match.b
        pred_end_offset = len(pred) - match.b - match.size
        score = match.size / (max([gold_end_offset, pred_end_offset]) + match.size + max([gold_start_offset, pred_start_offset]))
        scores.append(score)
    return mean(scores)


def quality(predicted: List[dict], expected: List[dict]):
    pred_dates, exp_dates, pred_names, exp_names, \
        pred_types, exp_types, pred_auths, exp_auths, pred_numbers, exp_numbers = ([] for _ in range(10))
    
    for pred, exp in zip(predicted, expected):

        pred_dates.append(pred['date'] if pred['date'] is not None else '')
        exp_dates.append(exp['date'])

        pred_numbers.append(pred['number'].lower() if pred['number'] is not None else '')
        exp_numbers.append(exp['number'].lower())

        pred_types.append(pred['type'] if pred['type'] is not None else '')
        exp_types.append(exp['type'])

        # authorities need to be normalized
        pred_auths.append(preprocess(pred['authority']) if pred['authority'] is not None else '')
        exp_auths.append(preprocess(exp['authority']))

        # names need to be normalized
        pred_names.append(preprocess(pred['name']) if pred['name'] is not None else '')
        exp_names.append(preprocess(exp['name']))

    date_accuracy = accuracy_score(exp_dates, pred_dates)
    
    number_accuracy = accuracy_score(exp_numbers, pred_numbers)

    type_f1 = f1_score(exp_types, pred_types, average='macro')

    name_jaccard = string_jaccard_metric(exp_names, pred_names)

    auth_jaccard = string_jaccard_metric(exp_auths, pred_auths)

    round_to = 10
    result = {
        'date_accuracy': float(round(date_accuracy, round_to)),
        'number_accuracy': float(round(number_accuracy, round_to)),
        'type_f1_score': float(round(type_f1, round_to)),
        'name_jaccard': float(round(name_jaccard, round_to)),
        'authority_jaccard': float(round(auth_jaccard, round_to))
    }
    result['subtasks_improves'] = subtasks_improves(result)
    
    return result
