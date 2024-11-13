from dataclasses import dataclass


@dataclass
class EstateRequest:
    api_key: str
    latitude: float
    longitude: float
