"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-07
Description: This module defines a contour layer class for quickmap.
"""
from cartopy import crs as ccrs
import folium
import matplotlib.pyplot as plt
import numpy as np
import json

from .Raster import Raster
from .utils import *


class ContourLayer(Raster):
    """
    以等值線表示的網格圖層。

    Attributes
        - geotiff_path: 網格資料的路徑。
        - band: 網格資料的band。
        - value_base: 等值線的基準值。
        - value_interval: 等值線的間隔值。
        - primary_contour_each: 每幾個首曲線繪製一個計曲線。*計曲線是加粗(2倍)且標記值的等值線，首曲線則是其他等值線。
        - line_color: 等值線的顏色。
        - line_width: 等值線的寬度。
        - font_size: 等值線標籤的字體大小。
        - font_color: 等值線標籤的字體顏色。
        - label_format: 等值線標籤的格式。
        - is_visible: 圖層是否顯示。
        - generalization: 將網格資料進行簡化（平均模糊）的程度，將會取代原始資料，不可復原。
        - meta: geotiff的meta資訊。
        - data: geotiff在該band的陣列。
        - crs: geotiff的crs。
        - transform: geotiff的transform。
        - shape: geotiff的shape。
        - west_bound: 西邊界。
        - east_bound: 東邊界。
        - south_bound: 南邊界。
        - north_bound: 北邊界。
        - max_of_original_data: 原始陣列的最大值。
        - min_of_original_data: 原始陣列的最小值。
        - mean_of_original_data: 原始陣列的平均值。
        - lat_list: 緯度列表。
        - lon_list: 經度列表。

    Methods
        - sliced_array_by_data_coordinate_system(x_left, x_right, y_bottom, y_top): 根據資料的座標系統切割後的numpy陣列。
        - slice_data_by_data_coordinate_system(x_left, x_right, y_bottom, y_top): 根據資料的座標系統切割本圖層。
        - generalize(size: int, normalize: bool): 對網格資料進行簡化（平均模糊），並完整紀錄簡化程度。
        - blur(range: int): 單純對陣列進行平均模糊。（不建議，建議使用generalize）
        - export_to_geojson_str(): 將等值線圖層匯出成geojson字串。
    """

    def __init__(self,
                 geotiff_path: str,
                 band: int = 1,
                 value_base: int | float = 0,
                 value_interval: int | float | str = "auto",
                 primary_contour_each: int = 5,
                 line_color: str = "#111111",
                 line_width: int | float = 0.4,
                 font_size: int | float = 8,
                 font_color: str = "#111111",
                 label_format: str = '%.1f',
                 generalization: int = 0,
                 is_visible: bool = True):
        """ 
        建立一個等值線圖層。

        Args
            - geotiff_path: str
                網格資料的路徑。
            - band: int
                網格資料的band，預設為1。
            - value_base: int|float
                等值線的基準值，預設為0。
            - value_interval: int|float|str
                等值線的間隔值，應為int或float，如果要自動計算，請輸入字串"auto"，預設為"auto"。
            - primary_contour_each: int|None
                每幾個首曲線繪製一個計曲線，預設為5，若為None則不繪製計曲線。
            - line_color: str
                等值線的顏色，預設為"#111111"。
            - line_width: int|float
                等值線的寬度，預設為0.4。
            - font_size: int|float
                等值線標籤的字體大小，預設為8。
            - font_color: str
                等值線標籤的字體顏色，預設為"#111111"。
            - label_format: str
                等值線標籤的格式，預設為'%.1f'。
            - generalization: int
                等值線的簡化程度，這項操作將直接改變原陣列，預設為0。
            - is_visible: bool
                圖層是否顯示，預設為True。

        Methods
            - set_default_interval(): 設定預設的等值線間隔值。
        """
        # init
        super().__init__(geotiff_path=geotiff_path,
                         band=band,
                         is_visible=is_visible)
        self.__value_base = None
        self.__value_interval = None
        self.__primary_contour_each = None
        self.__line_color = None
        self.__line_width = None
        self.__font_size = None
        self.__font_color = None
        self.__label_format = None

        # generalization
        if generalization != 0:
            self.generalize(size=generalization)

        # set attributes
        self.value_base = value_base
        self.value_interval = value_interval
        self.primary_contour_each = primary_contour_each
        self.line_color = line_color
        self.line_width = line_width
        self.font_size = font_size
        self.font_color = font_color
        self.label_format = label_format

    @property
    def value_base(self):
        return self.__value_base

    @value_base.setter
    def value_base(self, value_base: int | float):
        if not isinstance(value_base, (int, float)):
            raise TypeError("value_base必須是int或float。")
        self.__value_base = value_base

    @property
    def value_interval(self):
        return self.__value_interval

    @value_interval.setter
    def value_interval(self, value_interval: int | float):
        if value_interval == "auto":
            self.set_default_interval()
            return
        elif not isinstance(value_interval, (int, float)):
            raise TypeError("value_interval必須是int或float。")
        else:
            self.__value_interval = value_interval

    @property
    def primary_contour_each(self):
        return self.__primary_contour_each

    @primary_contour_each.setter
    def primary_contour_each(self, primary_contour_each: int):
        if primary_contour_each is None:
            self.__primary_contour_each = None
            return
        elif isinstance(primary_contour_each, int):
            check_positive(primary_contour_each)
            self.__primary_contour_each = primary_contour_each
            return
        else:
            raise TypeError("primary_contour_each必須是int或None。")

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
    def line_width(self, line_width: int | float):
        if not isinstance(line_width, (int, float)):
            raise TypeError("line_width必須是int或float。")
        check_positive(line_width)
        self.__line_width = line_width

    @property
    def font_size(self):
        return self.__font_size

    @font_size.setter
    def font_size(self, font_size: int | float):
        if not isinstance(font_size, (int, float)):
            raise TypeError("font_size必須是int或float。")
        check_positive(font_size)
        self.__font_size = font_size

    @property
    def font_color(self):
        return self.__font_color

    @font_color.setter
    def font_color(self, font_color: str):
        font_color = check_and_convert_color(font_color)
        self.__font_color = font_color

    @property
    def label_format(self):
        return self.__label_format

    @label_format.setter
    def label_format(self, label_format: str):
        if not isinstance(label_format, str):
            raise TypeError("label_format必須是str。")
        self.__label_format = label_format

    def set_default_interval(self):
        """
        設定預設的等值線間隔值。 
        """
        value_max = self.max_of_original_data
        value_min = self.min_of_original_data

        # 間距預設為20個等級
        self.value_interval = (value_max - value_min) / 15

    def export_to_geojson_str(self):
        """
        將等值線圖層匯出成geojson字串。

        Returns
            - str: geojson字串。
        """
        # 註：目前並無首曲線計曲線的差異，並且處理標籤
        # load attributes
        data = self.data  # 網格資料 numpy array
        value_base = self.value_base  # 等值線的基準值
        value_interval = self.value_interval
        min_of_original_data = self.min_of_original_data
        max_of_original_data = self.max_of_original_data
        crs = ccrs.PlateCarree()

        # Generate contour levels list
        levels_above_base = np.arange(value_base, max_of_original_data, value_interval).astype(float).tolist()
        levels_below_base = np.arange(value_base, min_of_original_data, -value_interval).astype(float).tolist()
        levels = levels_below_base[::-1][:-1] + levels_above_base

        # Generate contour lines
        X, Y = np.meshgrid(self.lon_list, self.lat_list)
        fig, ax = plt.subplots()
        CS = ax.contour(X, Y, data, levels=levels)
        plt.close(fig)  # Close the figure to free memory

        features = []

        for i, level in enumerate(CS.levels):
            segs = CS.allsegs[i]
            for seg in segs:
                coords = seg.tolist()
                geometry = {
                    "type": "LineString",
                    "coordinates": coords
                }
                feature = {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        "value": level
                    }
                }
                features.append(feature)

        # Create GeoJSON FeatureCollection
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        # Convert to string
        geojson_str = json.dumps(geojson)

        return geojson_str
