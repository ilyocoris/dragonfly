# pytest -s app/tests/test_endpoints.py
import os
import sys
import json
import uvicorn
import kafka_producer
from typing import List, Dict
from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
from bson.objectid import ObjectId


app = FastAPI()
producer = kafka_producer.initialize()


# @app.on_event("startup")
# def startup_event():
#     # on startup initialize kafka producer, async?
#     producer = KafkaProducer(
#         bootstrap_servers=[os.environ.get('KAFKA_BROKER_ADDRESS')],
#         key_serializer=lambda x: x.encode('utf-8'),
#         value_serializer=lambda x: json.dumps(x).encode('utf-8')
#     )


# @app.on_event("shutdown")
# def shutdown_event():
#     # blocking wait for all async messages to be sent, async?
#     producer.flush()
#     # close producer
#     producer.close(timeout=60)


class URLRequest(BaseModel):
    project_id: str
    url: str
    request_metadata: Dict = {}


class ScrapingRequest(BaseModel):
    url_list: List[URLRequest]


class URLResponse(URLRequest):
    scraping_id: str


class ScrapingResponse(BaseModel):
    scraping_list: List[URLResponse]


@app.post(
    "/process_urls",
    response_model=ScrapingResponse
)
def process_urls(request: ScrapingRequest):
    response = []
    for url in request.url_list:
        value = {
            "scraping_id": str(ObjectId()),
            "project_id": url.project_id,
            "url": url.url,
            "metadata": {"request": url.request_metadata}
        }
        producer.send(
            os.environ.get('TOPIC_SCRAPING'),
            key=url.project_id,
            value=value
        )
        response.append(URLResponse(**value))
    return ScrapingResponse(scraping_list=response)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6969)
