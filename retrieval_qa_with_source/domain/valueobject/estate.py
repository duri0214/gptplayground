from dataclasses import dataclass


@dataclass
class EstateRequest:
    api_key: str
    latitude: float
    longitude: float


@dataclass
class SchoolItem:
    school_name: str
    school_address: str


@dataclass
class SchoolDistrict:
    middle_school_items: list[SchoolItem]
    elementary_school_items: list[SchoolItem]


@dataclass
class Station:
    station: str
    company: str
    company_display_label: str
    rail: str
    distance_m: int


@dataclass
class StationInfo:
    stations: list[Station]


@dataclass
class PopulationChangeRate:
    rate: float
    display_label: str


@dataclass
class Population:
    current_population: int
    population_change_rate: PopulationChangeRate


@dataclass
class LandPrice:
    must_data: list[list[str]]


@dataclass
class EstateResponse:
    chiban_address: str
    chiban_area: int
    specific_use_district: str
    building_coverage_ratio: float
    floor_area_ratio: float
    school_district: SchoolDistrict
    station: StationInfo
    population: Population
    landprice: LandPrice
