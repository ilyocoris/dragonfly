import pytest
import os
import sys
for module_path in [os.path.abspath("/home/gus/Desktop/nlp-finance/")]:
    if module_path not in sys.path:
        sys.path.append(module_path)
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_process_urls_endpoint():
    body = {
        "url_list": [
            {
                "url_type": "subreddit",
                "url": "https://www.reddit.com/r/stocks/new/"
            },
            {
                "url_type": "subreddit",
                "url": "https://www.reddit.com/r/StockMarket/new/"
            }
        ]
    }
    response = client.post('/process_urls', json=body)
    assert response.status_code == 200
