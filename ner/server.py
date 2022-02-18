import os
import re
import json
import pandas as pd
from typing import Dict, List
from pymongo import MongoClient

import grpc
from concurrent import futures

import ner_pb2
import ner_pb2_grpc

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NER(ner_pb2_grpc.NERServicer):
    """
        This microservice receives text and finds entities dpeending on the domain. The domain is not a parameter by design, for different domains you should spin up different instances.
    """

    def __init__(self):

        # identifier of the version of the grpc service
        self.version = "naivekw_0"
        logger.info(
            "Initialization of NER GRPC Service version:" + self.version
        )
        # dictionary with all the entities to match
        self.entities = {}
        # domains
        self.domains = ["crypto"]  # finance
        # fetch all crypto and finance entities
        self.fetch_entities_from_db(self.domains)

    def ExtractEntities(self, request, context):
        try:
            ner_results = self._ner(request)
        except:
            ner_results = self._naive_ner(request=request)
        response_metadata = self.process_metadata(request.metadata)
        return ner_pb2.NerResponse(
            text=request.text,
            metadata=response_metadata,
            results=json.dumps(ner_results, ensure_ascii=False)
        )

    def process_metadata(self, metadata: str) -> str:
        metadata = json.loads(metadata)
        metadata["ner"] = {"version": self.version}
        return json.dumps(metadata)

    def fetch_entities_from_db(self, domains: List[str]) -> Dict:
        # get entities from db
        client = MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
        db = client[os.getenv("MONGO_DB_NAME")]
        mongo_entities = db[os.getenv("COLLECTION_ENTITIES")].find({
            "domain": {"$in": domains}})
        # add domains to entities
        for domain in domains:
            if domain not in self.entities.keys():
                self.entities[domain] = {}
        # format entities {domain:{entity:{synonims}}}
        for entity in mongo_entities:
            self.entities[entity["domain"]][entity["entity"]] = {
                "synonims": entity["synonims"],
                # "domain": entity["domain"]
            }

    def _naive_ner(self, request: ner_pb2.NerResponse) -> Dict:
        """
            State-of-the-art.
        """
        text = request.text
        for domain in self.domains:
            # if entities for a domain are not downloaded, do so
            if domain not in self.entities.keys():
                self.fetch_entities_from_db([domain])
            ner_matches = {}
            for entity in self.entities[domain].keys():
                synonims = self.entities[domain][entity]["synonims"]
                for synonim in synonims:
                    if synonim in text and len(synonim) > 1:
                        search = re.search(
                            r"[\s\,\.\?\!]" + synonim + r"[\s\,\.\?\!]", text)
                        if not search:
                            search = re.search(
                                r"^" + synonim + r"[\s\,\.\?\!]", text)
                        if search:
                            # TODO: ner_matches[entity]["matches"]
                            ner_matches[entity] = {
                                "span": [search.span()[0] + 1, search.span()[1] - 1],
                                "match": synonim,
                                "domain": domain
                            }
        return ner_matches

    def _ner(self, text: str) -> Dict:
        """
            RAMI: TRABAJA, PLASMA LAS PALABRAS HAZLAS BALAS.
            Input : text
            Returns:
                Dictionary with entities as keys and arbitrary hyperparameters for each key.
                Empty dictionary if nothing matched.
        """
        raise NotImplementedError


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ner_pb2_grpc.add_NERServicer_to_server(
        NER(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
