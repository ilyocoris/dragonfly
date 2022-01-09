import os
import json
import time
from kafka import KafkaConsumer


def initialize(
        topic_env: str,
        group_id_env: str) -> KafkaConsumer:
    '''
        Initialize kafka consumer, waiting for the kafka service to come fully up.
    '''
    consumer = None
    while consumer is None:
        try:
            consumer = KafkaConsumer(
                os.environ.get(topic_env),
                bootstrap_servers=[os.environ.get('KAFKA_BROKER_ADDRESS')],
                auto_offset_reset='earliest',
                # enable_auto_commit=True,
                group_id=os.environ.get(group_id_env),
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                key_deserializer=lambda x: x.decode('utf-8')
            )
        except:
            time.sleep(1)
            continue
    return consumer
