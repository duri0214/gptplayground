from dataclasses import asdict

import requests

from retrieval_qa_with_source.domain.valueobject.estate import EstateRequest


class EstateService:
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def post_estate_info(self, latitude: float, longitude: float):
        # リクエストデータをdataclassで作成
        data = EstateRequest(
            api_key=self.api_key,
            latitude=latitude,
            longitude=longitude,
        )

        # dataclassを辞書に変換してPOSTリクエスト
        response = requests.post(self.url, headers=self.headers, json=asdict(data))
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    service = EstateService(
        url="https://ty665ls8s5.execute-api.ap-northeast-1.amazonaws.com/prod/get-estate-additional-info",
        api_key="BxRsB#cd9~$E",
    )
    result = service.post_estate_info(latitude=35.652832, longitude=139.828491)
    print(result)
