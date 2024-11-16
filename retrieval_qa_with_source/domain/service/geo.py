import numpy as np
import rasterio
from rasterio.windows import Window

from retrieval_qa_with_source.domain.valueobject.geo import MetaData


class GeoService:
    @staticmethod
    def read_metadata(file_path: str) -> MetaData:
        """
        指定したGeoTIFFファイルを読み込み、メタデータをMetaDataオブジェクトに変換する。

        Args:
            file_path (str): GeoTIFFファイルのパス。

        Returns:
            MetaData: メタデータを格納したオブジェクト。
        """
        with rasterio.open(file_path) as dataset:
            meta = dataset.meta
            return MetaData(
                driver=meta["driver"],
                dtype=meta["dtype"],
                nodata=meta["nodata"],
                width=meta["width"],
                height=meta["height"],
                count=meta["count"],
                crs=meta["crs"],
                transform=meta["transform"],
            )

    @staticmethod
    def get_center_coordinates(file_path: str) -> tuple[float, float]:
        """
        指定したGeoTIFFファイルの中央ピクセルの緯度経度を取得する。

        Args:
            file_path (str): GeoTIFFファイルのパス。

        Returns:
            tuple[float, float]: 中央ピクセルの緯度と経度。
        """
        with rasterio.open(file_path) as dataset:
            width, height = dataset.width, dataset.height
            transform = dataset.transform

            # 中央ピクセルの行列インデックス
            center_x = width // 2
            center_y = height // 2

            # ピクセル座標を地理座標に変換
            lon, lat = rasterio.transform.xy(
                transform, center_y, center_x, offset="center"
            )
            return lat, lon

    @staticmethod
    def get_pixel_coordinates(
        file_path: str, pixel_x: int, pixel_y: int
    ) -> tuple[float, float]:
        """
        指定したピクセルの座標（緯度経度）を取得する。

        Args:
            file_path (str): GeoTIFFファイルのパス。
            pixel_x (int): X座標（横位置）のピクセル位置。
            pixel_y (int): Y座標（縦位置）のピクセル位置。

        Returns:
            tuple[float, float]: 指定したピクセル位置の緯度経度。
        """
        with rasterio.open(file_path) as dataset:
            transform = dataset.transform

            # ピクセル座標を地理座標に変換
            lon, lat = rasterio.transform.xy(
                transform, pixel_y, pixel_x, offset="center"
            )
            return lat, lon

    @staticmethod
    def read_band_as_array(file_path: str, band_index: int = 1) -> np.ndarray:
        """
        GeoTIFF ファイルの指定されたバンドを numpy 配列として読み込む。

        Args:
            file_path (str): GeoTIFFファイルのパス。
            band_index (int): 読み込むバンドのインデックス（デフォルトは1）。

        Returns:
            np.ndarray: 指定バンドのデータ。
        """
        with rasterio.open(file_path) as dataset:
            return dataset.read(band_index)

    @staticmethod
    def get_value_by_latlon(file_path: str, lon: float, lat: float) -> float:
        """
        緯度経度を指定してピンポイントの値を取得する。

        Args:
            file_path (str): GeoTIFFファイルのパス。
            lon (float): 経度。
            lat (float): 緯度。

        Returns:
            float: 指定した位置の値。
        """
        with rasterio.open(file_path) as dataset:
            py, px = dataset.index(lon, lat)
            return dataset.read(1)[py, px]

    @staticmethod
    def crop_by_bbox(
        file_path: str, min_lon: float, min_lat: float, max_lon: float, max_lat: float
    ) -> np.ndarray:
        """
        指定した緯度経度範囲のデータを切り取る。

        Args:
            file_path (str): GeoTIFFファイルのパス。
            min_lon (float): 左下の経度。
            min_lat (float): 左下の緯度。
            max_lon (float): 右上の経度。
            max_lat (float): 右上の緯度。

        Returns:
            np.ndarray: 指定範囲のデータ。
        """
        with rasterio.open(file_path) as src:
            py, px = src.index(min_lon, min_lat)
            py2, px2 = src.index(max_lon, max_lat)

            # 左上 (y: py2), 右下 (y: py) のピクセル範囲を指定
            window = Window.from_slices((py2, py + 1), (px, px2 + 1))
            return src.read(1, window=window)


# サンプル利用
if __name__ == "__main__":
    file_path = "sample_geo_picture.tif"  # GeoTIFFファイルのパス

    geo_service = GeoService()

    # メタデータを取得して表示
    metadata_vo = geo_service.read_metadata(file_path)
    print("Metadata:", metadata_vo)

    # 画像の中央ピクセルの緯度経度を取得して表示
    center_latlon = geo_service.get_center_coordinates(file_path)
    print(f"Center Latitude: {center_latlon[0]}, Center Longitude: {center_latlon[1]}")

    # 任意のピクセル位置(例えばピクセル位置 (100, 150)) の緯度経度を取得して表示
    pixel_latlon = geo_service.get_pixel_coordinates(file_path, 100, 150)
    print(f"Latitude: {pixel_latlon[0]}, Longitude: {pixel_latlon[1]}")

    # 指定されたバンドを numpy 配列として読み込んで表示
    band_array = geo_service.read_band_as_array(file_path, band_index=1)
    print("Band Array Shape:", band_array.shape)

    # 緯度経度を指定してピクセル値を取得して表示
    lon, lat = 136.902589, 37.391049  # 例: 任意の緯度経度
    value = geo_service.get_value_by_latlon(file_path, lon, lat)
    print(f"Value at ({lat}, {lon}): {value}")

    # 緯度経度範囲を指定して画像を切り取る
    min_lon, min_lat = 136.902589, 37.389831  # 左下（西南）
    max_lon, max_lat = 136.904030, 37.391049  # 右上（北東）
    cropped_data = geo_service.crop_by_bbox(
        file_path, min_lon, min_lat, max_lon, max_lat
    )
    print("Cropped Data Shape:", cropped_data.shape)
