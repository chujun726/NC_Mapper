"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-07
Description: This module defines some utility functions for quickmap.
"""

import geopandas as gpd
import matplotlib as mpl
import os
import pandas as pd
from typing import Union


def check_and_convert_color(color) -> tuple:
    """
    檢查並將顏色轉換為RGBA格式。

    Args
        - color: any
            顏色。

    Returns
        - color: tuple
    """
    try:
        color = mpl.colors.to_rgba(color)
        return color
    except ValueError:
        raise ValueError("無效的顏色。")


def check_lat(lat) -> None:
    """
    檢查緯度是否在範圍內。

    Args
        - lat: float
            緯度。

    Returns
        - None
    """
    if not isinstance(lat, (int, float)):
        raise TypeError("緯度必須是數字。")

    if not -90 <= lat <= 90:
        raise ValueError("緯度必須介於-90和90之間。")


def check_lon(lon) -> None:
    """
    檢查經度是否在範圍內。

    Args
        - lon: float
            經度。

    Returns
        - None
    """
    if not isinstance(lon, (int, float)):
        raise TypeError("經度必須是數字。")

    if not -180 <= lon <= 180:
        raise ValueError("經度必須介於-180和180之間。")


def check_positive(value: Union[int, float]) -> None:
    """
    檢查數字是否為正數。

    Args
        - value: int|float
            數字。

    Returns
        - None
    """
    if not isinstance(value, (int, float)):
        raise TypeError("數字必須是正數。")

    if value <= 0:
        raise ValueError("數字必須是正數。")


def check_not_negative(value: Union[int, float]) -> None:
    """
    檢查數字是否為非負數。

    Args
        - value: int|float
            數字。

    Returns
        - None
    """
    if not isinstance(value, (int, float)):
        raise TypeError("數字必須是非負數。")

    if value < 0:
        raise ValueError("數字必須是非負數。")


def check_nature_earth_resolution(resolution: str) -> None:
    """
    檢查是否為nature earth資料庫提供的解析度（10m, 50m, 110m）。

    Args
        - value: str
            解析度，以字串表示，例如"10m"。

    Returns
        - None
    """
    if resolution not in ["10m", "50m", "110m"]:
        raise ValueError("解析度必須是10m, 50m或110m。")


def check_dir_exist(path: str) -> None:
    """
    檢查目錄或文件所在目錄是否存在。

    Args
        - path: str
            目錄或文件路徑

    Returns
        - None
    """
    path = os.path.abspath(path)
    dir_path = os.path.dirname(path)
    is_file = os.path.isfile(path)
    is_dir = os.path.isdir(path)
    if is_file:
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"文件所在目錄不存在：{dir_path}")
    elif is_dir:
        if not os.path.exists(path):
            raise FileNotFoundError(f"目錄不存在：{path}")


def check_file_exist(path: str) -> None:
    """
    檢查路徑是否存在。

    Args
        - path: str
            文件路徑

    Returns
        - None
    """
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"路徑不存在：{path}")


def check_is_str(value: any) -> bool:
    """
    檢查是否為字串。

    Args
        - value: any
            任意值。

    Returns
        - bool
    """
    if not isinstance(value, str):
        raise TypeError("必須是字串。")
    return True


def check_column_exist_in_df(column_name: str, df: Union[pd.DataFrame, gpd.GeoDataFrame]) -> None:
    """
    檢查DataFrame是否包含指定的列。

    Args
        - column_name: str
            列名。
        - df: pd.DataFrame
            DataFrame。

    Returns
        - None
    """
    if column_name not in df.columns:
        raise ValueError(f"DataFrame中不存在列：{column_name}。")


def check_and_convert_to_float(value: any) -> float:
    """
    檢查並將值轉換為浮點數。

    Args
        - value: any
            任意值。

    Returns
        - float
    """
    try:
        value = float(value)
        return value
    except ValueError:
        raise ValueError("無效的數字。")
