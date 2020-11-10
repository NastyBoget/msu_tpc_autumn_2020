from solution import Solution
from eval_module import quality
import json

TRAIN_DIR = 'train/txts/'


if __name__ == "__main__":
    train = []
    with open("train/gold_labels.txt", "r") as read_file:
        for doc_info in read_file.readlines():
            doc_dict = json.loads(doc_info)
            docname = TRAIN_DIR + doc_dict['id'] + '.txt'
            with open(docname, 'r') as f:
                train.append((f.read(), doc_dict['label']))
    solution = Solution()
    test_data = [x[0] for x in train]
    test_labels = [x[1] for x in train]
    result = solution.predict(test_data)
    print(quality(result, test_labels))