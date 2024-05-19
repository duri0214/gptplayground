import os

import requests

from d_id.domain.valueobject.did import DidResponseData


class DidService:
    def __init__(self, source_url: str):
        self.source_url = source_url

    def create_new_stream(self):
        url = "https://api.d-id.com/talks/streams"

        payload = {
            "stream_warmup": "false",
            "source_url": self.source_url,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {os.environ.get('DID_API_KEY')}",
        }

        return DidResponseData(requests.post(url, json=payload, headers=headers))
