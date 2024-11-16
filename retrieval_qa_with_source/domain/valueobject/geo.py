from abc import abstractmethod, ABC
from dataclasses import dataclass

from affine import Affine
from rasterio.crs import CRS


@dataclass
class MetaData:
    """
    GeoTIFFファイルのメタデータを表現するクラス。

    Attributes:
        driver (str): データ形式 (例: 'GTiff')
        dtype (str): データ型 (例: 'uint16')
        nodata (None | float | int): データが存在しない領域を表す値。
        width (int): 画像の横幅（ピクセル単位）。
        height (int): 画像の縦幅（ピクセル単位）。
        count (int): 画像内のバンド（レイヤー）の数。
        crs (CRS | None): 座標参照系を表すオブジェクト。
            例: WGS 84の場合、`CRS.from_epsg(4326)`。
            Noneの場合、座標参照系が定義されていない。
        transform (Affine): アフィン変換行列。
            画像のピクセル座標と地理座標を関連付けるための行列。
    """

    driver: str
    dtype: str
    nodata: None | float | int
    width: int
    height: int
    count: int
    crs: CRS | None
    transform: Affine


class BaseCoords(ABC):
    @abstractmethod
    def get_coords(self, to_str: bool = False) -> tuple[float, float] | str:
        pass


class GoogleMapCoords(BaseCoords):
    def __init__(self, latitude: float, longitude: float):
        """
        googlemap は 緯度経度(lat, lng) で作成する
        """
        self.latitude = latitude
        self.longitude = longitude

    def get_coords(self, to_str: bool = False) -> tuple[float, float] or str:
        """
        :return: latitude, longitude
        """
        coordinates_tuple = self.latitude, self.longitude
        coordinates_str = f"{coordinates_tuple[0]}, {coordinates_tuple[1]}"
        return coordinates_tuple if to_str is False else coordinates_str
