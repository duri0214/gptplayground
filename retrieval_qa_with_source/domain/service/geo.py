import os

import numpy as np
import rasterio
from rasterio.windows import Window

from retrieval_qa_with_source.domain.valueobject.geo import MetaData, GoogleMapCoords


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
    def get_center_coordinates(file_path: str) -> GoogleMapCoords:
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
            return GoogleMapCoords(latitude=lat, longitude=lon)

    @staticmethod
    def get_pixel_coordinates(
        file_path: str, pixel_x: int, pixel_y: int
    ) -> GoogleMapCoords:
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
            return GoogleMapCoords(latitude=lat, longitude=lon)

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
    def get_value_by_coords(file_path: str, coords: GoogleMapCoords) -> float:
        """
        緯度経度を指定してピンポイントの値を取得する。

        Args:
            file_path (str): GeoTIFFファイルのパス。
            coords (GoogleMapCoords): 緯度経度。

        Returns:
            float: 指定した位置の値。
        """
        with rasterio.open(file_path) as dataset:
            py, px = dataset.index(coords.longitude, coords.latitude)
            return dataset.read(1)[py, px]

    @staticmethod
    def crop_by_bbox(
        file_path: str, min_coords: GoogleMapCoords, max_coords: GoogleMapCoords
    ) -> np.ndarray:
        """
        指定した緯度経度範囲のデータを切り取る。

        Args:
            file_path (str): GeoTIFFファイルのパス。
            min_coords (GoogleMapCoords): 左下の緯度経度。
            max_coords (GoogleMapCoords): 右上の緯度経度。

        Returns:
            np.ndarray: 指定範囲のデータ。
        """
        with rasterio.open(file_path) as src:
            py, px = src.index(min_coords.longitude, min_coords.latitude)
            py2, px2 = src.index(max_coords.longitude, max_coords.latitude)

            # 左上 (y: py2), 右下 (y: py) のピクセル範囲を指定
            window = Window.from_slices((py2, py + 1), (px, px2 + 1))
            return src.read(1, window=window)

    @staticmethod
    def rescale_and_save(file_path: str, brightness_factor: float = 1.0) -> None:
        """
        GeoTIFFファイルのデータを0～255にリスケールし、明るさを調整して保存する。
        保存時のファイル名は元ファイル名に '_rescaled' を付加する。

        Args:
            file_path (str): 入力GeoTIFFファイルのパス。
            brightness_factor (float): 明るさ調整係数（1.0でそのまま、値が大きいほど明るくなる）。
        """

        def rescale_data(data: np.ndarray, scale_factor: float) -> np.ndarray:
            """
            内部メソッド: データを0～255にリスケールし、明るさを調整する。

            Args:
                data (np.ndarray): 入力データ。
                scale_factor (float): 明るさ調整係数。

            Returns:
                np.ndarray: リスケールされたデータ。
            """
            data_min, data_max = np.percentile(
                data, [2, 98]
            )  # 上下2%をクリップしてリスケール
            rescaled = (data - data_min) / (data_max - data_min) * 255 * scale_factor
            rescaled = np.clip(rescaled, 0, 255)  # 値を0～255に制限
            return rescaled.astype(np.uint8)

        # 出力ファイル名を生成
        base_name, ext = os.path.splitext(file_path)
        output_path = f"{base_name}_rescaled{ext}"

        with rasterio.open(file_path) as dataset:
            # データの読み込み
            rescaled_data = rescale_data(
                data=dataset.read(1), scale_factor=brightness_factor
            )

            # メタデータの更新
            meta = dataset.meta.copy()
            meta.update(
                dtype="uint8", photometric="MINISBLACK"
            )  # グレースケール設定を追加

            # リスケール後のデータを新しいファイルに保存
            with rasterio.open(output_path, "w", **meta) as dst:
                dst.write(rescaled_data, 1)

        print(
            f"Rescaled GeoTIFF file saved as {output_path} with grayscale adjustment."
        )


# サンプル利用
if __name__ == "__main__":
    target_file_path = "sample_geo_picture.tif"  # GeoTIFFファイルのパス

    geo_service = GeoService()

    # メタデータを取得して表示
    metadata_vo = geo_service.read_metadata(target_file_path)
    print("Metadata:", metadata_vo)

    # 画像の中央ピクセルの緯度経度を取得して表示
    center_coords = geo_service.get_center_coordinates(target_file_path)
    print(
        f"Center Latitude: {center_coords.latitude}, Center Longitude: {center_coords.longitude}"
    )

    # 任意のピクセル位置(例えばピクセル位置 (100, 150)) の緯度経度を取得して表示
    pixel_coords = geo_service.get_pixel_coordinates(target_file_path, 100, 150)
    print(f"Latitude: {pixel_coords.latitude}, Longitude: {pixel_coords.longitude}")

    # 指定されたバンドを numpy 配列として読み込んで表示
    band_array = geo_service.read_band_as_array(target_file_path, band_index=1)
    print("Band Array Shape:", band_array.shape)

    # 緯度経度を指定してピクセル値を取得して表示
    target_coords = GoogleMapCoords(
        latitude=37.391049, longitude=136.902589
    )  # 任意の緯度経度
    value = geo_service.get_value_by_coords(target_file_path, target_coords)
    print(f"Value at ({target_coords.latitude}, {target_coords.longitude}): {value}")

    # 緯度経度範囲を指定して画像を切り取る
    target_coords = [
        GoogleMapCoords(latitude=37.389831, longitude=136.902589),  # 左下（西南）
        GoogleMapCoords(latitude=37.391049, longitude=136.904030),  # 右上（北東）
    ]
    cropped_data = geo_service.crop_by_bbox(
        file_path=target_file_path,
        min_coords=target_coords[0],
        max_coords=target_coords[1],
    )
    print("Cropped Data Shape:", cropped_data.shape)

    # 真っ黒写真回避｜GeoTIFFファイルのデータをリスケールして保存する
    geo_service.rescale_and_save(file_path=target_file_path)
