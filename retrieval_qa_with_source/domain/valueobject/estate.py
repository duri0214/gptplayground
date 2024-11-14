from dataclasses import dataclass


@dataclass
class EstateRequest:
    """
    地理座標に基づいて不動産情報を取得するリクエストデータモデル。

    Attributes:
        api_key (str): 認証用のAPIキー。
        latitude (float): 不動産の緯度。
        longitude (float): 不動産の経度。
    """

    api_key: str
    latitude: float
    longitude: float


@dataclass
class SchoolItem:
    """
    学区内の学校情報を表すデータモデル。

    Attributes:
        school_name (str): 学校名。
        school_address (str): 学校の住所。
    """

    school_name: str
    school_address: str


@dataclass
class SchoolDistrict:
    """
    学区情報を表すデータモデル。中学校と小学校のリストを含む。

    Attributes:
        middle_school_items (list[SchoolItem]): 中学校のリスト。
        elementary_school_items (list[SchoolItem]): 小学校のリスト。
    """

    middle_school_items: list[SchoolItem]
    elementary_school_items: list[SchoolItem]


@dataclass
class Station:
    """
    最寄り駅の情報を表すデータモデル。

    Attributes:
        station (str): 駅名。
        company (str): 鉄道会社の名前。
        company_display_label (str): 表示用の鉄道会社名。
        rail (str): 鉄道路線名。
        distance_m (int): 不動産から駅までの距離（メートル）。
    """

    station: str
    company: str
    company_display_label: str
    rail: str
    distance_m: int


@dataclass
class StationInfo:
    """
    最寄り駅情報のリストを表すデータモデル。

    Attributes:
        stations (list[Station]): 駅情報のリスト。
    """

    stations: list[Station]


@dataclass
class PopulationChangeRate:
    """
    人口増減率の情報を表すデータモデル。

    Attributes:
        rate (float): 人口増減率。
        display_label (str): 表示用の人口変化のラベル。
    """

    rate: float
    display_label: str


@dataclass
class Population:
    """
    人口情報を表すデータモデル。

    Attributes:
        current_population (int): 現在人口。
        population_change_rate (PopulationChangeRate): 人口増減率の詳細情報。
    """

    current_population: int
    population_change_rate: PopulationChangeRate


@dataclass
class LandPrice:
    """
    土地価格情報を表すデータモデル。

    Attributes:
        must_data (list[list[str]]): 必須の土地価格データ。公示価格や変動率などの情報を含む。
    """

    must_data: list[list[str]]


@dataclass
class EstateResponse:
    """
    不動産の詳細情報を表すレスポンスデータモデル。

    Attributes:
        chiban_address (str): 地番住所。
        chiban_area (int): 筆界面積（m²）。
        specific_use_district (str): 用途地域。
        building_coverage_ratio (float): 建蔽率（%）。
        floor_area_ratio (float): 容積率（%）。
        school_district (SchoolDistrict): 学区情報。
        station (StationInfo): 最寄り駅情報。
        population (Population): 人口情報。
        landprice (LandPrice): 土地価格情報。
    """

    chiban_address: str
    chiban_area: int
    specific_use_district: str
    building_coverage_ratio: float
    floor_area_ratio: float
    school_district: SchoolDistrict
    station: StationInfo
    population: Population
    landprice: LandPrice
