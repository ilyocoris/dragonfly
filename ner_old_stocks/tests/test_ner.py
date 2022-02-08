# pytest -s ner/tests/test_ner.py

import os
import sys
for module_path in [os.path.abspath("/home/gus/Desktop/nlp-finance/"), os.path.abspath("/home/gus/Desktop/nlp-finance/ner")]:
    if module_path not in sys.path:
        sys.path.append(module_path)

import json
import ner_pb2
from ner.server import FinanceNER


def test_extract_entities():
    finer = FinanceNER()
    request = ner_pb2.NerRequest(
        text="My personal bet is CTSH, they finna go up!"
    )
    response = finer.ExtractEntities(request, context=None)
    print(response)
    assert response.text == request.text
    assert response.results == json.dumps({
        "CTSH": {
            "span": [19, 23]
        }
    }, ensure_ascii=False)
