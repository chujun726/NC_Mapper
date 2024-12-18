"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-14
Description: This module defines a feature layer class for quickmap.
"""
from cartopy import crs as ccrs
import geopandas as gpd
from matplotlib import pyplot as plt
from pyproj import CRS

from .colormap import *
from .Layer import Layer
from .utils import *


class FeatureLayer(Layer):
    """
    圖徵資料圖層。

    Attributes
        - feature_path: str
            圖徵資料的路徑。
        - attribute_table: gpd.GeoDataFrame
            shapefile 的完整屬性資料。
        - value_column_name: str|None
            圖層的值所在的欄位名稱，如果為None，則無值。
        - data: dict
            shapefile 的屬性資料，只能包含geometry, value。
        - has_value: bool
            圖層是否有值。
        - value_color_dict: dict
            值和顏色的對應字典，格式為{值: 顏色}。
        - edge_default_color: str
            邊界的預設顏色。
        - edge_dynamic_color: bool
            邊界是否動態顏色(根據值變化)。
        - edge_width: float
            邊界的寬度。
        - marker: str
            點的標記。
        - face_default_color: str
            面的預設顏色。
        - face_dynamic_color: bool
            面是否動態顏色(根據值變化)。
        - value_type: str
            值的類型。（"continuous", "discrete"或"categorical"）
        - colorbar_ticks: list
            色條的標記點。
        - colorbar_extend: str
            色條是否延伸，可以是"neither"、"both"、"min"或"max"。
        - colorbar_title_label: str
            色條的標籤。
        - attribute_table: gpd.GeoDataFrame
            shapefile 的完整屬性資料。
        - crs: str
            shapefile 的crs。
        - is_visible: bool
            圖層是否顯示。
        - max_of_original_data: float
            原始資料的最大值。
        - min_of_original_data: float
            原始資料的最小值。
        - mean_of_original_data: float
            原始資料的平均值。
        - binary_map_is_recommended: bool
            是否推薦使用二元分類色階。
        - feature_type: str
            圖徵資料的類型。（Polygon, Point）

    Methods
        - set_mpl_color_map(color_map_name, min_value, max_value): 設置為matplotlib的色階。
        - set_default_color_map(): 恢復為預設色階。
    """
    # config
    available_value_types = ["continuous", "discrete"]  # , "categorical"]

    def __init__(self,
                 feature_path: str,
                 value_column_name: Union[str, None] = None,
                 value_color_dict: str = "auto",
                 edge_default_color: str = "#e15b5b",
                 edge_dynamic_color: bool = False,
                 edge_width: float = 0.5,
                 marker: str = "o",
                 face_default_color: str = "#f9eeee",
                 face_dynamic_color: bool = False,
                 value_type: str = "continuous",
                 colorbar_ticks: Union[list, str] = "auto",
                 colorbar_extend: str = "neither",
                 colorbar_title_label: str = "",
                 is_visible=True):
        """
        建立一個圖徵資料圖層。

        Args
            - feature_path: str
                圖徵資料的路徑。
            - value_column_name: str|None
                圖層的值所在的欄位名稱，如果為None，則無值。
            - value_color_dict: dict
                值和顏色的對應字典，格式為{值: 顏色}。
            - value_type: str
                值的類型，可以是"continuous"、"discrete"或"categorical"，預設為"continuous"。
            - edge_default_color: str
                邊界(或是點的標記)的預設顏色，預設為"black"。
            - edge_dynamic_color: bool
                邊界(或是點的標記)是否動態顏色(根據值變化)，預設為False。
            - edge_width: float
                邊界(或是點的標記)的寬度，預設為0.5。
            - marker: str
                點的標記，預設為"o"。
            - face_default_color: str
                面的預設顏色，預設為"gray"。
            - face_dynamic_color: bool
                面是否動態顏色(根據值變化)，預設為False。
            - colorbar_ticks: list
                色條的標記點，預設為"auto"。
            - colorbar_extend: str
                色條是否延伸，可以是"neither"、"both"、"min"或"max"，預設為"neither"。
            - colorbar_title_label: str
                色條的標籤，預設為空。
            - is_visible: bool
                圖層是否顯示。
        """
        # init
        self.__feature_path = None
        self.__attribute_table = None
        self.__value_column_name = None
        self.__value_color_dict = None
        self.__value_type = None
        self.__edge_default_color = None
        self.__edge_dynamic_color = None
        self.__edge_width = None
        self.__marker = None
        self.__face_default_color = None
        self.__face_dynamic_color = None
        self.__colorbar_ticks = None
        self.__colorbar_extend = None
        self.__colorbar_title_label = None

        super().__init__(is_visible)
        self.feature_path = feature_path
        self.attribute_table = self.__load_attribute_table()
        self.value_column_name = value_column_name
        self.value_color_dict = value_color_dict
        self.value_type = value_type
        self.edge_default_color = edge_default_color
        self.edge_dynamic_color = edge_dynamic_color
        self.edge_width = edge_width
        self.marker = marker
        self.face_default_color = face_default_color
        self.face_dynamic_color = face_dynamic_color
        self.colorbar_ticks = colorbar_ticks
        self.colorbar_extend = colorbar_extend
        self.colorbar_title_label = colorbar_title_label

        self._convert_gdf_to_geographic_crs()

    @property
    def feature_path(self):
        return self.__feature_path

    @feature_path.setter
    def feature_path(self, value):
        if self.__feature_path is not None:
            raise AttributeError("feature_path is read-only.")

        check_is_str(value)
        check_file_exist(value)

        self.__feature_path = value

    @property
    def attribute_table(self):
        return self.__attribute_table

    @attribute_table.setter
    def attribute_table(self, table):
        if self.__attribute_table is not None:
            raise AttributeError("attribute_table is read-only.")

        if not isinstance(table, gpd.GeoDataFrame):
            raise TypeError("attribute_table must be a GeoDataFrame.")

        self.__attribute_table = table

    def __load_attribute_table(self):
        return gpd.read_file(self.feature_path)

    @property
    def value_column_name(self):
        return self.__value_column_name

    @value_column_name.setter
    def value_column_name(self, value):
        if value is None:
            self.__value_column_name = None
            return

        check_is_str(value)
        check_column_exist_in_df(value, self.attribute_table)

        self.__value_column_name = value
        self.value_color_dict = 'auto'
        self.colorbar_ticks = 'auto'

    @property
    def data(self) -> gpd.GeoDataFrame:
        gdf = self.attribute_table
        if self.value_column_name is not None:
            gdf = gdf[[self.value_column_name, "geometry"]]
            gdf = gdf.rename(columns={self.value_column_name: "value"})
        elif self.value_column_name is None:
            gdf = gdf[["geometry"]]
        return gdf

    @property
    def has_value(self):
        return self.value_column_name is not None

    @property
    def value_color_dict(self):
        if self.value_column_name is None:
            value_color_dict = dict()
        else:
            value_color_dict = self.__value_color_dict
        return value_color_dict

    @value_color_dict.setter
    def value_color_dict(self, value_color_dict: Union[dict, str]):
        if self.value_column_name is None:
            value_color_dict = dict()
        elif value_color_dict == "auto":
            value_color_dict = calculate_continuous_color_map(self.min_of_original_data, self.max_of_original_data)

        for value, color in value_color_dict.items():
            color = check_and_convert_color(color)
            value_color_dict[value] = color
        self.__value_color_dict = value_color_dict

    @property
    def edge_default_color(self):
        return self.__edge_default_color

    @edge_default_color.setter
    def edge_default_color(self, color):
        color = check_and_convert_color(color)
        self.__edge_default_color = color

    @property
    def edge_dynamic_color(self):
        if self.has_value:
            return self.__edge_dynamic_color
        elif not self.has_value:
            return False

    @edge_dynamic_color.setter
    def edge_dynamic_color(self, value):
        if not isinstance(value, bool):
            raise TypeError("edge_dynamic_color must be a bool.")
        self.__edge_dynamic_color = value

    @property
    def edge_width(self):
        return self.__edge_width

    @edge_width.setter
    def edge_width(self, value):
        value = check_and_convert_to_float(value)
        check_positive(value)
        self.__edge_width = value

    @property
    def marker(self):
        return self.__marker

    @marker.setter
    def marker(self, value):
        check_is_str(value)
        if value not in plt.Line2D.markers:
            raise ValueError(f"marker must be one of {list(plt.Line2D.markers.keys())}.")
        self.__marker = value

    @property
    def face_default_color(self):
        return self.__face_default_color

    @face_default_color.setter
    def face_default_color(self, value):
        check_is_str(value)
        self.__face_default_color = value

    @property
    def face_dynamic_color(self):
        if self.value_column_name is None:
            return False
        return self.__face_dynamic_color

    @face_dynamic_color.setter
    def face_dynamic_color(self, value):
        if not isinstance(value, bool):
            raise TypeError("face_dynamic_color must be a bool.")
        self.__face_dynamic_color = value

    @property
    def value_type(self):
        if self.value_column_name is None:
            return None
        return self.__value_type

    @value_type.setter
    def value_type(self, value):
        if value not in self.available_value_types:
            raise ValueError(f"value_type must be one of {self.available_value_types}.")
        self.__value_type = value

    @property
    def colorbar_ticks(self):
        if self.value_column_name is None:
            return list()
        return self.__colorbar_ticks

    @colorbar_ticks.setter
    def colorbar_ticks(self, value):
        if value == "auto" and self.binary_map_is_recommended:
            value = calculate_binary_color_map_ticks(self.min_of_original_data, self.max_of_original_data)
        elif value == "auto" and not self.binary_map_is_recommended:
            value = calculate_continuous_color_map_ticks(self.min_of_original_data, self.max_of_original_data)
        self.__colorbar_ticks = value

    @property
    def colorbar_extend(self):
        return self.__colorbar_extend

    @colorbar_extend.setter
    def colorbar_extend(self, value):
        if value not in ["neither", "both", "min", "max"]:
            raise ValueError("colorbar_extend must be one of ['neither', 'both', 'min', 'max'].")
        self.__colorbar_extend = value

    @property
    def colorbar_title_label(self):
        return self.__colorbar_title_label

    @colorbar_title_label.setter
    def colorbar_title_label(self, value):
        check_is_str(value)
        self.__colorbar_title_label = value

    @property
    def crs(self):
        return ccrs.PlateCarree()

    @property
    def max_of_original_data(self):
        if self.value_column_name is None:
            return 0
        return self.attribute_table[self.value_column_name].max()

    @property
    def min_of_original_data(self):
        if self.value_column_name is None:
            return 0
        return self.attribute_table[self.value_column_name].min()

    @property
    def mean_of_original_data(self):
        if self.value_column_name is None:
            return 0
        return self.attribute_table[self.value_column_name].mean()

    @property
    def binary_map_is_recommended(self):
        if self.value_column_name is None:
            return False
        return self.mean_of_original_data < 0.5

    @property
    def feature_type(self):
        return self.attribute_table.geom_type[0]

    def _convert_gdf_to_geographic_crs(self):
        gdf = self.__attribute_table
        if gdf.crs.is_geographic:
            pass
        else:
            gdf = gdf.to_crs(CRS.from_epsg(4326))
        self.__attribute_table = gdf
