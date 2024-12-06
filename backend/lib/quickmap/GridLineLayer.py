"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-07
Description: This module defines a gridline layer class for quickmap.
"""
from .Layer import Layer
from .utils import *


class GridLineLayer(Layer):
    """
    地圖的經緯度格線圖層。

    Attributes
        - plot_at_lat: 繪製的緯度列表。
        - plot_at_lon: 繪製的經度列表。
        - line_color: 格線的顏色。
        - line_width: 格線的寬度（pixel）。
        - label_size: 經緯度標籤的大小。
        - label_color: 經緯度標籤的顏色。
        - label_weight: 經緯度標籤的粗細。
        - label_font: 經緯度標籤的字體。
        - is_visible: 圖層是否顯示。

    Class Methods
        - from_list(plot_at_lat: list, plot_at_lon: list): 直接由列表建立一個格線圖層。
        - from_interval(lat_base: float, lon_base: float, lat_interval: float, lon_interval: float): 由緯度基準、經度基準、緯度間隔和經度間隔建立一個格線圖層。
    """

    def __init__(self,
                 plot_at_lat: list = [lat for lat in range(-90, 91, 10)],
                 plot_at_lon: list = [lon for lon in range(-180, 361, 10)],
                 line_color='gray',
                 line_width=0.5,
                 label_size=10,
                 label_color='#1E1E1E',
                 label_weight=300,
                 label_font='Open-Sans',
                 is_visible=True):
        """
        建立一個格線圖層。

        Args
            - plot_at_lat: 繪製的緯度列表，預設為從 -80 到 80，間隔 10 度。
            - plot_at_lon: 繪製的經度列表，預設為從 -180 到 180，間隔 10 度。
            - line_color: 格線的顏色，預設為黑色。
            - line_width: 格線的寬度（pixel），預設為 1。
            - label_size: 經緯度標籤的大小，預設為 10。
            - label_color: 經緯度標籤的顏色，預設為黑色。
            - label_weight: 經緯度標籤的粗細，預設為 400。
            - label_font: 經緯度標籤的字體，預設為Open-Sans。
            - is_visible: 圖層是否顯示，預設為 True。
        """
        # init
        super().__init__(is_visible)
        self.__plot_at_lat = None
        self.__plot_at_lon = None
        self.__line_color = None
        self.__line_width = None
        self.__label_size = None
        self.__label_color = None
        self.__label_weight = None
        self.__label_font = None

        # set attributes
        self.plot_at_lat = plot_at_lat
        self.plot_at_lon = plot_at_lon
        self.line_color = line_color
        self.line_width = line_width
        self.label_size = label_size
        self.label_color = label_color
        self.label_weight = label_weight
        self.label_font = label_font

    @classmethod
    def from_list(cls, plot_at_lat: list, plot_at_lon: list):
        return cls(plot_at_lat, plot_at_lon)

    @classmethod
    def from_interval(cls, lat_base: float, lon_base: float, lat_interval: float, lon_interval: float):
        # calculate the lat list
        lat_list = []
        lat = lat_base
        while lat <= 90:
            lat_list.append(lat)
            lat += lat_interval
        lat = lat_base - lat_interval
        while lat >= -90:
            lat_list.append(lat)
            lat -= lat_interval
        lat_list = sorted(lat_list)

        # calculate the lon list
        lon_list = []
        lon = lon_base
        while lon <= 180:
            lon_list.append(lon)
            lon += lon_interval
        lon = lon_base - lon_interval
        while lon >= -180:
            lon_list.append(lon)
            lon -= lon_interval
        lon_list = sorted(lon_list)

        return cls(lat_list, lon_list)

    @property
    def plot_at_lat(self):
        return self.__plot_at_lat

    @plot_at_lat.setter
    def plot_at_lat(self, plot_at_lat: list):
        for lat in plot_at_lat:
            check_lat(lat)
        self.__plot_at_lat = plot_at_lat

    @property
    def plot_at_lon(self):
        return self.__plot_at_lon

    @plot_at_lon.setter
    def plot_at_lon(self, plot_at_lon: list):
        for lon in plot_at_lon:
            check_lon(lon)
        self.__plot_at_lon = plot_at_lon

    @property
    def line_color(self):
        return self.__line_color

    @line_color.setter
    def line_color(self, line_color: str):
        line_color = check_and_convert_color(line_color)
        self.__line_color = line_color

    @property
    def line_width(self):
        return self.__line_width

    @line_width.setter
    def line_width(self, line_width: int):
        check_positive(line_width)
        self.__line_width = line_width

    @property
    def label_size(self):
        return self.__label_size

    @label_size.setter
    def label_size(self, label_size: int):
        check_positive(label_size)
        self.__label_size = label_size

    @property
    def label_color(self):
        return self.__label_color

    @label_color.setter
    def label_color(self, label_color: str):
        label_color = check_and_convert_color(label_color)
        self.__label_color = label_color

    @property
    def label_weight(self):
        return self.__label_weight

    @label_weight.setter
    def label_weight(self, label_weight: int):
        check_positive(label_weight)
        self.__label_weight = label_weight

    @property
    def label_font(self):
        return self.__label_font

    @label_font.setter
    def label_font(self, label_font: str):
        if not isinstance(label_font, str):
            raise TypeError("label_font必須是str。")
        self.__label_font = label_font
