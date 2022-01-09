'''
    The Analyzer is consumer subscribed to the TOPIC_CHUNKS topic on Kafka.
    For each chunk, it will call the appropiate microservices and store the relevant results to the TOPIC_RESULTS and mongodb.
'''
import os
import json
import grpc
from typing import Dict
from datetime import datetime, timezone

import mongodb
import kafka_consumer
import kafka_producer

import ner_pb2
import ner_pb2_grpc
import sa_pb2
import sa_pb2_grpc

ner_channel = grpc.insecure_channel(
    os.environ.get("NER_SERVER_ADDRESS")
)
ner_stub = ner_pb2_grpc.FinanceNERStub(ner_channel)
# sa grpc client
sa_channel = grpc.insecure_channel(
    os.environ.get("SA_SERVER_ADDRESS")
)
sa_stub = sa_pb2_grpc.FinanceSAStub(sa_channel)

# define consumer
consumer = kafka_consumer.initialize(
    topic_env='TOPIC_CHUNKS',
    group_id_env='CONSUMER_GROUP_CHUNKS'
)

# define kafka producer
producer = kafka_producer.initialize()


def publish_result(chunk_event: Dict, ner_results: Dict, sa_results: Dict) -> None:
    chunk_value = json.loads(chunk_event.value)
    producer.send(
        os.environ.get('TOPIC_RESULTS'),
        key=chunk_event.key,
        value=json.dumps({
            "chunk_id": chunk_value["chunk_id"],
            "project_id": chunk_value["project_id"],
            "text": chunk_value["text"],
            "text_metadata": chunk_value["text_metadata"],
            "ner_results": json.dumps(ner_results),
            "sa_results": json.dumps(sa_results)
        })
    )

# "{\"chunk_id\": \"61d4d59a9f3862000107ef28\", \"project_id\": \"000000000000000000000000\", \"scraping_id\": \"61d4d59430ad680001f1a7be\", \"text\": \"You know what this means: PUBG2 is fucked\", \"text_metadata\": \"{\\\"timestamp\\\": 1641315209.0, \\\"comment_id\\\": \\\"hr8drts\                    "type": "opinion",


db = mongodb.get_db_connection()

# TODO : this should be done async!!!
for event in consumer:
    chunk = json.loads(event.value)
    ner_response = ner_stub.ExtractEntities(
        ner_pb2.NerRequest(
            text=chunk["text"],
            metadata=chunk["text_metadata"]
        )
    )
    ner_results = json.loads(ner_response.results)
    if ner_results:
        sa_response = sa_stub.SentimentAnalysis(
            sa_pb2.SaRequest(
                text=chunk["text"],
                metadata=chunk["text_metadata"]
            )
        )
        sa_results = json.loads(sa_response.results)
        print(event.value)
        # publish to kafka
        publish_result(
            chunk_event=event,
            ner_results=ner_results,
            sa_results=sa_results
        )
        # TODO: move this to another consumer
        # publish events to mongo time series TM
        for entity in ner_results:
            text_metadata = json.loads(chunk["text_metadata"])
            # timestamp from unix to utc, for mongo time series TM to recognize
            utc_ts = datetime.fromtimestamp(
                int(text_metadata["timestamp"]) / 1000, tz=timezone.utc)
            db[os.environ.get("COLLECTION_EVENTS")].insert_one({
                "event": {
                    "entity": entity,
                    "type": "opinion",
                    "origin": "reddit",
                    "value": sa_results["label"],
                },
                "timestamp": utc_ts,
                "metadata": {
                    "scraping_id": chunk["scraping_id"],
                    "chunk_id": chunk["chunk_id"]
                }
            })
