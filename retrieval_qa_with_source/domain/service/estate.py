import os
from dataclasses import asdict

import requests
from dotenv import load_dotenv

from retrieval_qa_with_source.domain.valueobject.estate import (
    EstateRequest,
    EstateResponse,
    LandPrice,
    PopulationChangeRate,
    Population,
    StationInfo,
    Station,
    SchoolItem,
    SchoolDistrict,
)

# .env ファイルを読み込む
load_dotenv()


class EstateService:
    def __init__(self, url: str):
        self.api_key = os.getenv("ESTATE_API_KEY")
        if not self.api_key:
            raise ValueError("ESTATE_API_KEY is not set or is empty.")

        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def post_estate_info(self, latitude: float, longitude: float) -> EstateResponse:
        data = EstateRequest(
            api_key=self.api_key,
            latitude=latitude,
            longitude=longitude,
        )

        # dataclassを辞書に変換してPOSTリクエスト
        response = requests.post(self.url, headers=self.headers, json=asdict(data))
        response.raise_for_status()

        return self._parse_estate_response(response.json())

    @staticmethod
    def _parse_estate_response(data: dict) -> EstateResponse:
        # 学校区情報
        school_district = SchoolDistrict(
            middle_school_items=[
                SchoolItem(**item)
                for item in data["schoolDistrict"]["middleSchoolItems"]
            ],
            elementary_school_items=[
                SchoolItem(**item)
                for item in data["schoolDistrict"]["elementarySchoolItems"]
            ],
        )

        # 駅情報
        stations = [
            Station(
                station=station["station"],
                company=station["company"],
                company_display_label=station["companyDisplayLabel"],
                rail=station["rail"],
                distance_m=station["distanceM"],
            )
            for station in data["station"]["stations"]
        ]
        station_info = StationInfo(stations=stations)

        # 人口情報
        population = Population(
            current_population=data["population"]["currentPopulation"],
            population_change_rate=PopulationChangeRate(
                rate=data["population"]["populationChangeRate"]["rate"],
                display_label=data["population"]["populationChangeRate"][
                    "displayLabel"
                ],
            ),
        )

        # 土地価格情報
        land_price = LandPrice(must_data=data["landprice"]["mustData"])

        return EstateResponse(
            chiban_address=data.get("chibanAddress", ""),
            chiban_area=data.get("chibanArea", 0),
            specific_use_district=data.get("specificUseDistrict", ""),
            building_coverage_ratio=data.get("buildingCoverageRatio", 0.0),
            floor_area_ratio=data.get("floorAreaRatio", 0.0),
            school_district=school_district,
            station=station_info,
            population=population,
            landprice=land_price,
        )


if __name__ == "__main__":
    service = EstateService(
        url="https://ty665ls8s5.execute-api.ap-northeast-1.amazonaws.com/prod/get-estate-info"
    )
    result = service.post_estate_info(latitude=35.662832, longitude=139.828491)
    print(result)
