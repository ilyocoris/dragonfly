'''
    The Scraper is consumer subscribed to the TOPIC_SCRAPING topic on Kafka.
    On each scraping event, it will call the appropiate scrapping microservice, and publish the received stream of chunks of text on the TOPIC_CHUNKS topic.
'''
import os
import json
import bson
from typing import Dict

import mongodb
import kafka_consumer
import kafka_producer

import grpc
import scraper_pb2
import scraper_pb2_grpc

# scraping grpc client
scraper_channel = grpc.insecure_channel(
    os.environ.get("SCRAPER_SERVER_ADDRESS")
)
scraper_stub = scraper_pb2_grpc.ScraperStub(scraper_channel)

# define consumer
consumer = kafka_consumer.initialize(
    topic_env='TOPIC_SCRAPING',
    group_id_env='CONSUMER_GROUP_SCRAPING'
)

# define kafka producer
producer = kafka_producer.initialize()

# publishes chunk of text to the chunk topic


def publish_chunk(chunk: scraper_pb2.ScraperResponse) -> None:
    '''
        Publishes chunk of scraped text to the TOPIC_CHUNK topic.
    '''
    chunk_id = str(bson.objectid.ObjectId())
    producer.send(
        os.environ.get('TOPIC_CHUNKS'),
        key=chunk_id,
        value=json.dumps({
            "chunk_id": chunk_id,
            "project_id": chunk.project_id,
            "scraping_id": chunk.scraping_id,
            "text": chunk.text,
            "metadata": chunk.metadata
        })
    )


def new_reddit_comment(url: str, chunk: scraper_pb2.ScraperResponse) -> bool:
    '''
        Checks that the comment that contains the chunk has not already been scraped.
        If it is new, it stores the id on the mongodb and returns True so it is published to the chunks topic.
        If the comment had already been scraped, it returns False.
    '''
    db = mongodb.get_db_connection()
    text_metadata = json.loads(chunk.metadata)["scraper"]["text"]
    db_post = db["scraping_reddit"].find_one(
        {
            "post": text_metadata["post_id"]
        }
    )
    if not db_post:
        db["scraping_reddit"].insert_one({
            "scraping": chunk.scraping_id,
            "project": chunk.project_id,
            "subreddit": url,
            "metadata": metadata,
            "post": text_metadata["post_id"],
            "comments": [text_metadata["comment_id"]]
        })
    elif text_metadata["comment_id"] not in db_post["comments"]:
        db["scraping_reddit"].update_one({"scraping": chunk.scraping_id, "post": text_metadata["post_id"]}, {
                                         "$set": {"comments": db_post["comments"] + [text_metadata["comment_id"]]}})
    else:
        # comment already scrapped
        return False
    return True


for event in consumer:
    scraping_job = event.value
    url = scraping_job["url"]
    metadata = scraping_job["metadata"]
    request = scraper_pb2.ScraperRequest(
        project_id=scraping_job["project_id"],
        scraping_id=scraping_job["scraping_id"],
        url=url,
        metadata=json.dumps(metadata)
    )
    if "type" in metadata["request"]:
        if metadata["request"]["type"] == "subreddit":
            for chunk in scraper_stub.ScrapeReddit(request):
                if new_reddit_comment(url, chunk):
                    publish_chunk(chunk)
