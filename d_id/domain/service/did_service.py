import os

import requests

from d_id.domain.valueobject.did import DidResponseData


class DidService:
    def __init__(self, source_url: str):
        self.source_url = source_url
        self.stream = self._create_stream()
        self._start_stream()

    def _create_stream(self):
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
        res = requests.post(url, json=payload, headers=headers)
        print(res.text)

        return DidResponseData(res)

    def _start_stream(self):
        url = f"https://api.d-id.com/talks/streams/{self.stream.id}/sdp"

        payload = {
            "answer": {
                "type": "answer",
                "sdp": self.stream.offer.sdp,
            },
            "session_id": self.stream.session_id,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {os.environ.get('DID_API_KEY')}",
        }

        res = requests.post(url, json=payload, headers=headers)
        print(res.status_code, res.json())
