"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-07
Description: This module defines a shading layer class for quickmap.
"""
from .colormap import *
from .Raster import Raster
from .utils import *


class ShadingLayer(Raster):
    """
    以塗色表示的網格圖層。

    Attributes
        - geotiff_path: 網格資料的路徑。
        - band: 網格資料的band。
        - value_color_dict: 值和顏色的對應字典，格式為{值: 顏色}。
        - value_type: 值的類型，可能是"continuous"、"discrete"或"categorical"。
        - colorbar_ticks: 色條的標記點。
        - colorbar_extend: 色條是否延伸，可以是"neither"、"both"、"min"或"max"。
        - colorbar_title_label: 色條的標籤。
        - interpolation: 插值方法。
        - generalization: 將網格資料進行簡化（平均模糊）的程度，將會取代原始資料，不可復原。
        - meta: geotiff的meta資訊。
        - data: geotiff在該band的陣列。
        - crs: geotiff的crs。
        - transform: geotiff的transform。
        - shape: geotiff的shape。
        - is_visible: 圖層是否顯示。
        - west_bound: 西邊界。
        - east_bound: 東邊界。
        - south_bound: 南邊界。
        - north_bound: 北邊界。
        - max_of_original_data: 原始陣列的最大值。
        - min_of_original_data: 原始陣列的最小值。
        - mean_of_original_data: 原始陣列的平均值。
        - lat_list: 緯度列表。
        - lon_list: 經度列表。
        - binary_map_is_recommended: 是否推薦使用二元分類色階。

    Methods
        - sliced_array_by_data_coordinate_system(x_left, x_right, y_bottom, y_top): 根據資料的座標系統切割後的numpy陣列。
        - slice_data_by_data_coordinate_system(x_left, x_right, y_bottom, y_top): 根據資料的座標系統切割本圖層。
        - set_mpl_color_map(color_map_name, min_value, max_value): 設置為matplotlib的色階。
        - set_default_color_map(): 恢復為預設色階。
        - generalize(size: int, normalize: bool): 對網格資料進行簡化（平均模糊），並完整紀錄簡化程度。
        - blur(range: int): 單純對陣列進行平均模糊。（不建議，建議使用generalize）
    """
    # config
    available_value_types = ["continuous", "discrete"]  # , "categorical"]

    def __init__(self,
                 geotiff_path: str,
                 band: int = 1,
                 value_color_dict: str = "auto",
                 value_type: str = "continuous",
                 colorbar_ticks: Union[list, str] = "auto",
                 colorbar_extend: str = "neither",
                 colorbar_title_label: str = "",
                 interpolation: str = "nearest",
                 is_visible=True):
        """
        建立一個塗色網格圖層。

        Args
            - geotiff_path: 網格資料的路徑。
            - band: 網格資料的band，預設為1。
            - value_color_dict: 值和顏色的對應字典，格式為{值: 顏色}，預設為"auto"。
            - value_type: 值的類型，可以是"continuous"、"discrete"或"categorical"，預設為"continuous"。
            - colorbar_ticks: 色條的標記點，預設為"auto"。
            - colorbar_extend: 色條是否延伸，可以是"neither"、"both"、"min"或"max"，預設為"neither"。
            - colorbar_title_label: 色條的標籤，預設為空。
            - interpolation: 插值方法，可以是"nearest"、"bilinear"或"cubic"，預設為"nearest"。
            - is_visible: 圖層是否顯示。
        """
        # init
        super().__init__(geotiff_path=geotiff_path,
                         band=band,
                         is_visible=is_visible)
        self.__value_color_dict = None
        self.__value_type = None
        self.__colorbar_ticks = None
        self.__colorbar_extend = None
        self.__colorbar_title_label = None
        self.__interpolation = None

        # set default value_color_dict
        binary_map_is_recommended = self.binary_map_is_recommended
        generate_value_color_dict = value_color_dict == "auto"
        if generate_value_color_dict and binary_map_is_recommended:
            value_color_dict = self._calculte_binary_color_map_from_array()
        elif generate_value_color_dict and not binary_map_is_recommended:
            value_color_dict = self._calculate_continuous_color_map_from_array()

        # set default colorbar_ticks
        binary_map_is_recommended = self.binary_map_is_recommended
        generate_colorbar_ticks = colorbar_ticks == "auto"
        if generate_colorbar_ticks and binary_map_is_recommended:
            colorbar_ticks = calculate_binary_color_map_ticks(self.min_of_original_data, self.max_of_original_data)
        elif generate_colorbar_ticks and not binary_map_is_recommended:
            colorbar_ticks = calculate_continuous_color_map_ticks(self.min_of_original_data, self.max_of_original_data)

        # set attributes
        self.value_color_dict = value_color_dict
        self.value_type = value_type
        self.colorbar_ticks = colorbar_ticks
        self.colorbar_extend = colorbar_extend
        self.colorbar_title_label = colorbar_title_label
        self.interpolation = interpolation

    @property
    def value_color_dict(self):
        return self.__value_color_dict

    @value_color_dict.setter
    def value_color_dict(self, value_color_dict: dict):
        for value, color in value_color_dict.items():
            color = check_and_convert_color(color)
            value_color_dict[value] = color
        self.__value_color_dict = value_color_dict

    @property
    def value_type(self):
        return self.__value_type

    @value_type.setter
    def value_type(self, value_type: str):
        if value_type not in self.available_value_types:
            raise ValueError(f"value_type必須是{self.available_value_types}之一。")
        self.__value_type = value_type

    @property
    def colorbar_ticks(self):
        return self.__colorbar_ticks

    @colorbar_ticks.setter
    def colorbar_ticks(self, colorbar_ticks: Union[list, str]):
        if isinstance(colorbar_ticks, list):
            colorbar_ticks = colorbar_ticks
        elif isinstance(colorbar_ticks, np.ndarray):
            colorbar_ticks = colorbar_ticks.tolist()
        elif colorbar_ticks == "auto":
            colorbar_ticks = calculate_continuous_color_map_ticks(self.min_of_original_data, self.max_of_original_data)
        else:
            raise ValueError("colorbar_ticks必須是list或'auto'。")
        self.__colorbar_ticks = colorbar_ticks

    @property
    def colorbar_extend(self):
        return self.__colorbar_extend

    @colorbar_extend.setter
    def colorbar_extend(self, colorbar_extend: str):
        if colorbar_extend not in ["neither", "both", "min", "max"]:
            raise ValueError("colorbar_extend必須是'neither', 'both', 'min'或'max'之一。")
        self.__colorbar_extend = colorbar_extend

    @property
    def colorbar_title_label(self):
        return self.__colorbar_title_label

    @colorbar_title_label.setter
    def colorbar_title_label(self, colorbar_title_label: str):
        if not isinstance(colorbar_title_label, str):
            raise TypeError("colorbar_title_abel必須是str。")
        self.__colorbar_title_label = colorbar_title_label

    @property
    def interpolation(self):
        return self.__interpolation

    @interpolation.setter
    def interpolation(self, interpolation: str):
        if interpolation not in ["nearest", "bilinear", "cubic"]:
            raise ValueError("interpolation必須是'nearest', 'bilinear'或'cubic'之一。")
        self.__interpolation = interpolation

    @property
    def binary_map_is_recommended(self) -> bool:
        """
        是否推薦使用二元分類色階。

        Returns
            - is_recommended: bool
                是否推薦使用二元分類色階。
        """
        # get the max and min value
        max_value = self.max_of_original_data
        min_value = self.min_of_original_data

        # calculate the color map
        if (abs(max_value) - self.mean_of_original_data > 3 * self.mean_of_original_data) and \
           (abs(min_value) - self.mean_of_original_data > 3 * self.mean_of_original_data):
            return True
        else:
            return False

    def _calculte_binary_color_map_from_array(self) -> dict:
        """
        從圖層陣列計算二元分類色階。

        Returns
            - value_color_dict: dict
                值和顏色的對應字典，格式為{值: 顏色}。
        """
        # get the max and min value
        max_value = self.max_of_original_data
        min_value = self.min_of_original_data

        # calculate the color map
        value_color_dict = calculate_binary_color_map(min_value, max_value)
        return value_color_dict

    def _calculate_continuous_color_map_from_array(self, cmap_name="jet") -> dict:
        """
        從圖層陣列計算連續色階。

        Args
            - cmap_name: str
                色階名稱。

        Returns
            - value_color_dict: dict
                值和顏色的對應字典，格式為{值: 顏色}。
        """
        # get the max and min value
        max_value = self.max_of_original_data
        min_value = self.min_of_original_data

        # calculate the color map
        value_color_dict = calculate_continuous_color_map(min_value, max_value, cmap_name)

        return value_color_dict

    def set_mpl_color_map(self, color_map_name: str, min_value: Union[float, None] = None, max_value: Union[float, None] = None) -> dict:
        """
        設置為matplotlib的色階。

        Args
            - color_map_name: str
                色階名稱，可以是matplotlib的色階名稱。
            - min_value: float
                最小值，預設為None，也就是使用原始數據的最小值。
            - max_value: float
                最大值，預設為None，也就是使用原始數據的最大值。

        Returns
            - value_color_dict: dict
                值和顏色的對應字典，格式為{值: 顏色}。
        """
        # get the max and min value
        if min_value is None:
            min_value = self.min_of_original_data
        if max_value is None:
            max_value = self.max_of_original_data

        # calculate the color map
        value_color_dict = calculate_continuous_color_map(min_value, max_value, color_map_name)

        self.value_color_dict = value_color_dict

        return value_color_dict

    def set_default_color_map(self) -> dict:
        """
        根據當前陣列數值恢復為預設色階。

        Returns
            - value_color_dict: dict
                值和顏色的對應字典，格式為{值: 顏色}。
        """
        # calculate the color map
        binary_map_is_recommended = self.binary_map_is_recommended
        if binary_map_is_recommended:
            value_color_dict = self._calculte_binary_color_map_from_array()
        elif not binary_map_is_recommended:
            value_color_dict = self._calculate_continuous_color_map_from_array()

        self.value_color_dict = value_color_dict

        return value_color_dict
