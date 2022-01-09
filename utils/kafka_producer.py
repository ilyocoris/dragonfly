import os
import json
import time
from kafka import KafkaProducer


def initialize() -> KafkaProducer:
    '''
        Initialize kafka producer, waiting for the kafka service to come fully up.
    '''
    producer = None
    while producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[os.environ.get('KAFKA_BROKER_ADDRESS')],
                key_serializer=lambda x: x.encode('utf-8'),
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
        except:
            time.sleep(1)
            continue
    return producer
