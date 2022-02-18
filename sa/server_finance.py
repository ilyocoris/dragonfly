import os
import json
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

import grpc
from concurrent import futures

import sa_pb2
import sa_pb2_grpc

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SA(sa_pb2_grpc.SAServicer):
    def __init__(self):
        self.version = "distilroberta-finsa_0"
        logger.info(
            "Initialization of SA GRPC Service version: " + self.version
        )
        self.model = "models/distilroberta-finetuned-financial-news-sentiment-analysis"
        self._load_sa_pipeline(
            model_path_or_name=self.model
        )

    def _load_sa_pipeline(self, model_path_or_name: str):
        '''
            Initializes a huggingface sentiment-analysis pipeline for a model.
        '''
        sa_tokenizer = AutoTokenizer.from_pretrained(
            model_path_or_name)

        sa_model = AutoModelForSequenceClassification.from_pretrained(
            model_path_or_name)

        self.sa_pipeline = pipeline(
            "sentiment-analysis",
            model=sa_model,
            tokenizer=sa_tokenizer
        )

    def SentimentAnalysis(self, request, context):
        # TODO: manage sequences longer than 512 tokens
        pipeline_result = self.sa_pipeline(request.text[:200])[0]
        metadata = json.loads(request.metadata)
        metadata["sa"] = {
            "version": self.version,
            "model": self.model
        }
        metadata = json.dumps(metadata)
        return sa_pb2.SaResponse(
            text=request.text,
            metadata=metadata,
            results=json.dumps(
                pipeline_result,
                ensure_ascii=False
            )
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sa_pb2_grpc.add_SAServicer_to_server(
        SA(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
