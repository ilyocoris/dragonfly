import os
import sys
# for module_path in [os.path.abspath("/home/gus/Desktop/nlp-finance/"), os.path.abspath("/home/gus/Desktop/nlp-finance/ner"), os.path.abspath("/home/gus/Desktop/nlp-finance/sa")]:
#     if module_path not in sys.path:
#         sys.path.append(module_path)


import re
import grpc
import praw
import json

import ner_pb2
import ner_pb2_grpc
import sa_pb2
import sa_pb2_grpc

from pydantic import BaseModel


class Text(BaseModel):
    text: str
    text_metadata: str


class Event(BaseModel):
    timestamp: str
    company: str
    sentiment: str
    mongo_id: str


class EventExtractor():
    def __init__(self):
        print("Starting Event Extractor")
        self._initialize_reddit_scraper()
        # TODO: parametrize this to the request
        self.reddit_posts_limit = 10
        self._initialize_ner_stub()
        self._initialize_sa_stub()

    def process_url(self, request_url):
        for text in self._get_text_chunks(request_url):
            ner_response = self.ner_stub.ExtractEntities(
                ner_pb2.NerRequest(
                    text=text.text
                )
            )
            sa_response = self.sa_stub.SentimentAnalysis(
                sa_pb2.SaRequest(
                    text=text.text
                )
            )
            for event in self._build_event(text, ner_response, sa_response):
                yield event

    def _build_event(self, text: Text, ner_response: ner_pb2.NerResponse, sa_response: sa_pb2.SaResponse) -> Event:
        print(ner_response)
        print(sa_response.results)
        text_metadata = json.loads(text.text_metadata)
        timestamp = text_metadata["timestamp"]
        ner_results = json.loads(ner_response.results)
        sa_results = json.loads(sa_response.results)
        for company in ner_results.keys():
            yield Event(**{
                "timestamp": timestamp,
                "company": company,
                "sentiment": sa_results["label"],
                "mongo_id": text.text,
            })

    def _get_text_chunks(self, request_url) -> Text:
        if request_url.url_type == "subreddit":
            for comment in self._subreddit_comments(request_url.url):
                yield comment
        else:
            raise NotImplementedError

    def _initialize_reddit_scraper(self):
        self.reddit = praw.Reddit(
            client_id=os.environ.get("REDDIT_APP_ID"),
            client_secret=os.environ.get("REDDIT_APP_SECRET"),
            user_agent=os.environ.get(
                "REDDIT_APP_NAME") + ' by ' + os.environ.get("REDDIT_USERNAME")
        )

    def _subreddit_comments(self, url: str) -> Text:
        """
            Parameters:
                url : the url of a subreddit
            Returns:
                yields all comments found with some metadata in a Text class
        """
        # TODO: think about reddit urls
        subreddit_name = re.search("/r/([^/]+)", url)[1]
        # TODO: may not want to get new
        posts = self.reddit.subreddit(subreddit_name).new(
            limit=self.reddit_posts_limit)
        # TODO: parallelize this
        for post in posts:
            submission = self.reddit.submission(id=post.id)
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                yield Text(**{
                    "text": comment.body,
                    "text_metadata": json.dumps({
                        "timestamp": comment.created,
                        # "parent_comment_id": comment.parend_id,
                        "comment_id": comment.id,
                        "post_id": post.id
                    }, ensure_ascii=False)
                })

    def _initialize_ner_stub(self):
        ner_channel = grpc.insecure_channel(
            os.environ.get("NER_SERVER_ADDRESS")
        )
        self.ner_stub = ner_pb2_grpc.NERStub(ner_channel)

    def _initialize_sa_stub(self):
        sa_channel = grpc.insecure_channel(
            os.environ.get("SA_SERVER_ADDRESS")
        )
        self.sa_stub = sa_pb2_grpc.SAStub(sa_channel)
