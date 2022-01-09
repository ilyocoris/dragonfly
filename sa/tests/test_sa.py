# pytest -s sa/tests/test_sa.py

import os
import sys
from typing import Text
for module_path in [os.path.abspath("/home/gus/Desktop/nlp-finance/"), os.path.abspath("/home/gus/Desktop/nlp-finance/sa")]:
    if module_path not in sys.path:
        sys.path.append(module_path)

import json
from sa.server import FinanceSA

import sa_pb2
import sa_pb2_grpc


def test_sentiment_analysis():
    finsta = FinanceSA()
    request = sa_pb2.SaRequest(
        text="I think CRM stocks are sinking big time. Everybody dip!"
    )
    response = finsta.SentimentAnalysis(request, context=None)
    print(response)
    assert response.text == request.text
    sa_results = json.loads(response.results)
    assert sa_results["label"] == "negative"
