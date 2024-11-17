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
    """
    座標を表すベースクラス。緯度と経度を持つ。

    メソッド:
    get_coords : 座標を取得します。戻り値の形式を指定することもできます。

    抽象メソッド:
    get_coords
    """

    def __init__(self, latitude: float, longitude: float):
        """
        BaseCoords クラスのインスタンスを生成します。

        パラメータ:
        latitude (float): 緯度
        longitude (float): 経度
        """
        self.latitude = latitude
        self.longitude = longitude

    @abstractmethod
    def to_tuple(self) -> tuple[float, float]:
        pass

    @abstractmethod
    def to_str(self) -> str:
        pass


class GoogleMapCoords(BaseCoords):
    def to_tuple(self) -> tuple[float, float]:
        return self.latitude, self.longitude

    def to_str(self) -> str:
        return f"{self.latitude}, {self.longitude}"
