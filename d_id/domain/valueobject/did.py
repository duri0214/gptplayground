import requests


class DidResponseData:
    class _Offer:
        def __init__(self, offer_data: dict):
            self.type = offer_data.get("type")
            self.sdp = offer_data.get("sdp")

    class _IceServer:
        def __init__(self, ice_server_data: dict):
            self.urls = ice_server_data.get("urls")
            if isinstance(self.urls, str):
                self.urls = [self.urls]
            else:
                self.urls = self.urls
            self.username = ice_server_data.get("username")
            self.credential = ice_server_data.get("credential")

    def __init__(
        self,
        response: requests.models.Response,
    ):
        if response.status_code == 401:
            raise Exception("不正なリクエストです。資格情報を確認してください。")
        response_data = response.json()
        self.id = response_data.get("id")
        self.offer = self.Offer(response_data.get("offer"))
        self.ice_servers = [self.IceServer(x) for x in response_data.get("ice_servers")]
        self.session_id = response_data.get("session_id")
