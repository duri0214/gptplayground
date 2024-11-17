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
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

    @abstractmethod
    def to_tuple(self) -> tuple[float, float]:
        """
        座標をタプル形式で取得します。具体的な順序はサブクラスによります。

        Returns:
            tuple[float, float]: 座標を表すタプル
        """
        pass

    @abstractmethod
    def to_str(self) -> str:
        """
        座標を文字列形式で取得します。具体的な順序はサブクラスによります。

        Returns:
            str: 座標を表す文字列
        """
        pass


class GoogleMapCoords(BaseCoords):
    """
    Google Map 用の座標変換クラス。BaseCoordsを継承します。

    メソッド:
    to_tuple: 座標をタプル形式で取得します。戻り値は (緯度,経度) 形式です。
    to_str : 座標を文字列形式で取得します。戻り値は "緯度, 経度" 形式です。
    """

    def to_tuple(self) -> tuple[float, float]:
        return self.latitude, self.longitude

    def to_str(self) -> str:
        return f"{self.latitude}, {self.longitude}"
