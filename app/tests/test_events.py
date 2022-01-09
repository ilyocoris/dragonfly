# pytest -s app/tests/test_events.py

import os
import sys
for module_path in [os.path.abspath("/home/gus/Desktop/nlp-finance/"), os.path.abspath("/home/gus/Desktop/nlp-finance/ner"), os.path.abspath("/home/gus/Desktop/nlp-finance/sa")]:
    if module_path not in sys.path:
        sys.path.append(module_path)

import json

from app.src.events import EventExtractor, Text

from sa import sa_pb2
from ner import ner_pb2


def test_build_event():
    ee = EventExtractor()
    text = "I think CRM stocks are sinking big time. Everybody dip!"
    events = ee._build_event(
        text=Text(
            text=text,
            text_metadata=json.dumps({
                "timestamp": "the_time_is_now"
            })
        ),
        ner_response=ner_pb2.NerResponse(
            text=text,
            ner_results=json.dumps({
                "CRM": {
                    "span": [0, 0]
                }
            })
        ),
        sa_response=sa_pb2.SaResponse(
            text=text,
            sa_results=json.dumps({
                "label": "negative"
            })
        )
    )
    for event in events:
        assert event.timestamp == "the_time_is_now"
        assert event.company == "CRM"
        assert event.sentiment == "negative"
        assert event.mongo_id == text
