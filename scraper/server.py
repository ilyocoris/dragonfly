import os
import re
import json
import praw
from typing import Dict
from pydantic import BaseModel

import grpc
from concurrent import futures

import scraper_pb2
import scraper_pb2_grpc

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TextChunk(BaseModel):
    text: str
    metadata: str


class Scraper(scraper_pb2_grpc.ScraperServicer):
    def __init__(self):
        self.reddit = None
        self.version = "praw-mongo_0"
        logger.info(
            "Initialization of Scraper GRPC Service version: " + self.version
        )

    def ScrapeReddit(self, request, context):
        if not self.reddit:
            self._initialize_reddit_scraper(
                json.loads(request.metadata)["request"])
        for comment in self._get_subreddit_comments(url=request.url):
            # add scraper metadata
            metadata = json.loads(request.metadata)
            metadata["scraper"] = {
                "text": json.loads(comment.metadata),
                "version": self.version
            }
            metadata = json.dumps(metadata)
            # yield results
            yield scraper_pb2.ScraperResponse(
                project_id=request.project_id,
                scraping_id=request.scraping_id,
                text=comment.text,
                metadata=metadata
            )

    def _initialize_reddit_scraper(self, url_metadata: Dict):
        self.reddit = praw.Reddit(
            client_id=os.environ.get("REDDIT_APP_ID"),
            client_secret=os.environ.get("REDDIT_APP_SECRET"),
            user_agent=os.environ.get(
                "REDDIT_APP_NAME") + ' by ' + os.environ.get("REDDIT_USERNAME")
        )
        if "post_limit" in url_metadata:
            self.reddit_posts_limit = url_metadata["post_limit"]
        else:
            self.reddit_posts_limit = 10

    def _get_subreddit_comments(self, url: str) -> TextChunk:
        """
            Parameters:
                url : the url of a subreddit
            Returns:
                yields all comments found with some metadata in a TextChunk class
        """
        # TODO: think about reddit urls
        subreddit_name = re.search("/r/([^/]+)", url)[1]
        logger.info("Scraping subreddit", subreddit_name)
        # TODO: may not want to get new
        posts = self.reddit.subreddit(subreddit_name).new(
            limit=self.reddit_posts_limit)
        # TODO: parallelize this
        for post in posts:
            submission = self.reddit.submission(id=post.id)
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                yield TextChunk(**{
                    "text": comment.body,
                    "metadata": json.dumps({
                        "timestamp": comment.created,
                        # "parent_comment_id": comment.parend_id,
                        "comment_id": comment.id,
                        "post_id": post.id
                    }, ensure_ascii=False)
                })


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    scraper_pb2_grpc.add_ScraperServicer_to_server(
        Scraper(), server)
    server.add_insecure_port('[::]:50051')
    print("Start scraping server.")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
