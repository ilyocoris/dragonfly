import re
import json
import pandas as pd
from typing import Dict

import grpc
from concurrent import futures

import ner_pb2
import ner_pb2_grpc


class FinanceNER(ner_pb2_grpc.FinanceNERServicer):
    def __init__(self):
        df = pd.read_csv(
            # "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
            "s&p.csv"
        )
        # self.company_names = list(df["Name"])
        self.company_symbols = list(df["Symbol"])

    def ExtractEntities(self, request, context):
        try:
            ner_results = self._ner(request.text)
        except:
            ner_results = self._naive_ner(request.text)
        return ner_pb2.NerResponse(
            text=request.text,
            metadata=request.metadata,
            results=json.dumps(ner_results, ensure_ascii=False)
        )

    def _naive_ner(self, text: str) -> Dict:
        """
            State-of-the-art.
        """
        ner_matches = {}
        for company in self.company_symbols:
            if company in text and len(company) > 1:
                search = re.search(
                    r"[\s\,\.\?\!]" + company + r"[\s\,\.\?\!]", text)
                if not search:
                    search = re.search(r"^" + company + r"[\s\,\.\?\!]", text)
                if search:
                    ner_matches[company] = {
                        "span": [search.span()[0] + 1, search.span()[1] - 1]
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
    ner_pb2_grpc.add_FinanceNERServicer_to_server(
        FinanceNER(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
