"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-25
Description: This module defines a Raster class for quickmap.
"""
from numba import njit, prange
import numpy as np
import rasterio
import scipy

from .Layer import Layer
from .utils import *


class Raster(Layer):
    """
    網格資料物件。

    Attributes
        - geotiff_path: 網格資料的路徑。
        - band: 網格資料的band。
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
        - nodata_value: 無效值。

    Methods
        - sliced_array_by_data_coordinate_system(x_left, x_right, y_bottom, y_top): 根據資料的座標系統切割後的numpy陣列。
        - slice_data_by_data_coordinate_system(x_left, x_right, y_bottom, y_top): 根據資料的座標系統切割本圖層。
        - generalize(size: int, normalize: bool): 對網格資料進行簡化（平均模糊），並完整紀錄簡化程度。
        - blur(range: int): 單純對陣列進行平均模糊。（不建議，建議使用generalize）
    """

    def __init__(self,
                 geotiff_path: str,
                 band: int = 1,
                 is_visible: bool = True):
        """
        建立一個網格資料物件。

        Args
            - geotiff_path: str
                網格資料的路徑。
            - band: int
                網格資料的band，預設為1。
            - is_visible: bool
                圖層是否顯示，預設為True。
        """
        # init
        super().__init__(is_visible)
        self.__geotiff_path = None
        self.__band = None
        self.__meta = None
        self.__generalization = 0

        # read geotiff
        with rasterio.open(geotiff_path) as src:
            self.__meta = src.meta
            try:
                self.__data = src.read(band).astype(np.float32)
                self.__meta["dtype"] = "float32"
            except IndexError:
                raise ValueError(f"band {band}不存在。")
            self.__crs = src.crs
            self.__transform = src.transform

        # corp data if data's latitude over 90 or less than -90
        if self.__crs.to_epsg() == 4326:
            while self.__transform[5] > 90:
                # clip first row of data
                self.__data = self.__data[1:, :]
                self.__transform = rasterio.Affine(self.__transform[0], self.__transform[1], self.__transform[2],
                                                   self.__transform[3], self.__transform[4], self.__transform[5] + self.__transform[4])
            while self.__transform[5] < -90:
                # clip last row of data
                self.__data = self.__data[:-1, :]
                self.__transform = rasterio.Affine(self.__transform[0], self.__transform[1], self.__transform[2],
                                                   self.__transform[3], self.__transform[4], self.__transform[5] - self.__transform[4])

        # mask nodata with nan
        nodata_value = self.__meta["nodata"]
        if nodata_value is not None:
            self.__data = np.where(self.__data == nodata_value, np.nan, self.__data)
        self.__meta["nodata"] = np.nan

        # set attributes
        self.geotiff_path = geotiff_path
        self.band = band

    @property
    def geotiff_path(self):
        return self.__geotiff_path

    @geotiff_path.setter
    def geotiff_path(self, geotiff_path: str):
        # can't be modified
        if self.__geotiff_path is not None:
            raise ValueError("geotiff_path不能被修改。")

        # check
        check_file_exist(geotiff_path)
        if not geotiff_path.endswith(".tif"):
            raise ValueError("geotiff_path必須是一個tif文件。")

        # set
        self.__geotiff_path = geotiff_path

    @property
    def band(self):
        return self.__band

    @band.setter
    def band(self, band: int):
        if not isinstance(band, int):
            raise TypeError("band必須是int。")
        check_positive(band)
        self.__band = band

    @property
    def meta(self):
        return self.__meta

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data: np.ndarray):
        if not isinstance(data, np.ndarray):
            raise TypeError("data必須是np.ndarray。")
        if data.shape != self.shape:
            raise ValueError("data的shape必須與原始數據的shape相同。")
        self.__data = data

    @property
    def shape(self):
        return self.__data.shape

    @property
    def crs(self):
        return self.__crs

    @property
    def transform(self):
        return self.__transform

    @property
    def west_bound(self):
        """
        獲取西邊界。

        Returns
            - west_bound: float
                西邊界。
        """
        return self.transform[2]

    @property
    def east_bound(self):
        """
        獲取東邊界。

        Returns
            - east_bound: float
                東邊界。
        """
        return self.transform[2] + self.transform[0] * self.shape[1]

    @property
    def south_bound(self):
        """
        獲取南邊界。

        Returns
            - south_bound: float
                南邊界。
        """
        return self.transform[5] + self.transform[4] * self.shape[0]

    @property
    def north_bound(self):
        """
        獲取北邊界。

        Returns
            - north_bound: float
                北邊界。
        """
        return self.transform[5]

    @property
    def max_of_original_data(self) -> float:
        """
        獲取原始陣列的最大值。

        Returns
            - max_value: float
                最大值。
        """
        max_value = float(np.nanmax(self.data))
        return max_value

    @property
    def min_of_original_data(self) -> float:
        """
        獲取原始陣列的最小值。

        Returns
            - min_value: float
                最小值。
        """
        min_value = float(np.nanmin(self.data))
        return min_value

    @property
    def mean_of_original_data(self) -> float:
        """
        獲取原始陣列的平均值。

        Returns
            - mean_value: float
                平均值。
        """
        mean_value = float(np.nanmean(self.data))
        return mean_value

    @property
    def lat_list(self):
        """
        獲取緯度列表。

        Returns
            - lat_list: list
                緯度列表。
        """
        return np.linspace(self.north_bound, self.south_bound, self.shape[0]).tolist()

    @property
    def lon_list(self):
        """
        獲取經度列表。

        Returns
            - lon_list: list
                經度列表。
        """
        return np.linspace(self.west_bound, self.east_bound, self.shape[1]).tolist()

    @property
    def nodata_value(self):
        return np.nan

    @property
    def generalization(self):
        return self.__generalization

    def generalize(self, size: int, normalize: bool = False):
        # check
        if self.generalization is None or self.generalization == 0:
            if not isinstance(size, int):
                raise TypeError("generalization必須是int。")
            if size < 0:
                raise ValueError("generalization必須是正整數。")
        else:
            raise ValueError("若以generalize過，不能再被修改。")

        # generalization
        if size != 0:
            self.blur_data(size, normalize=normalize)
            self.__generalization = size

    def sliced_array_by_data_coordinate_system(self, x_left: Union[int, float], x_right: Union[int, float], y_bottom: Union[int, float], y_top: Union[int, float]) -> tuple:
        """
        根據資料的座標系統切割數據。

        Args
            - x_left: float
                切割框的左邊界。
            - x_right: float
                切割框的右邊界。
            - y_bottom: float
                切割框的下邊界。
            - y_top: float
                切割框的上邊界。

        Returns
            - tuple
                - sliced_data: ndarray
                    切割後的數據。
                - transform: Affine
                    切割後的transform。
        """
        # get the window
        window = rasterio.windows.from_bounds(x_left, y_bottom, x_right, y_top, self.transform)

        # slice data
        x_from = int(window.col_off)
        x_to = int(window.col_off + window.width)
        y_from = int(window.row_off)
        y_to = int(window.row_off + window.height)
        sliced_data = self.data[y_from:y_to, x_from:x_to]

        # calc transform
        x_res = self.transform[0]
        y_res = self.transform[4]
        x_offset = self.transform[2] + x_from * x_res
        y_offset = self.transform[5] + y_from * y_res
        sliced_transform = rasterio.Affine(x_res, 0, x_offset, 0, y_res, y_offset)

        return (sliced_data, sliced_transform)

    def slice_data_by_data_coordinate_system(self, x_left: Union[int, float], x_right: Union[int, float], y_bottom: Union[int, float], y_top: Union[int, float]):
        """
        根據資料的座標系統切割本圖層，本操作會直接異動本圖層的數據。

        Args
            - x_left: float
                切割框的左邊界。
            - x_right: float
                切割框的右邊界。
            - y_bottom: float
                切割框的下邊界。
            - y_top: float
                切割框的上邊界。

        Returns
            None
        """
        # update data and transform
        sliced_array, sliced_transform = self.sliced_array_by_data_coordinate_system(x_left, x_right, y_bottom, y_top)
        self.__data = sliced_array
        self.__transform = sliced_transform

    def blur_data(self, size: int, normalize: bool = False):
        """
        對數據進行高斯模糊，本操作會直接異動本圖層的數據。

        Args
            - size: int
            高斯模糊的範圍。
            - normalize: bool
            是否對值進行調整，例如，如果原本的值介於0~10之間，模糊後的值只介於2~8之間，則重新縮放至0~10之間。

        Returns
            None
        """
        # check
        if not isinstance(size, int):
            raise TypeError("range必須是int。")
        check_positive(size)

        # load data
        original_data = self.__data

        # blur
        blurred_data = self.moving_average_2d_skip_nan_numba(original_data, window_size=size)

        # normalize
        if normalize:
            original_min = np.nanmin(original_data)
            original_max = np.nanmax(original_data)
            blurred_min = np.nanmin(blurred_data)
            blurred_max = np.nanmax(blurred_data)
            a = (original_max - original_min) / (blurred_max - blurred_min)
            b = original_min - a * blurred_min
            blurred_data = blurred_data * a + b

        # update data
        self.__data = blurred_data

    @staticmethod
    @njit(parallel=True)
    def moving_average_2d_skip_nan_numba(data, window_size=3):
        rows, cols = data.shape
        pad_size = window_size // 2
        result = np.empty((rows, cols), dtype=np.float64)

        for i in prange(rows):
            for j in range(cols):
                i_min = max(i - pad_size, 0)
                i_max = min(i + pad_size + 1, rows)
                j_min = max(j - pad_size, 0)
                j_max = min(j + pad_size + 1, cols)

                window = data[i_min:i_max, j_min:j_max].flatten()
                center = data[i, j]

                if np.isnan(center):
                    result[i, j] = np.nan
                else:
                    valid_values = window[~np.isnan(window)]
                    if valid_values.size > 0:
                        result[i, j] = valid_values.mean()
                    else:
                        result[i, j] = np.nan

        return result

    def export_geotiff(self, output_path: str):
        """
        將本圖層輸出為geotiff文件。

        Args
            - output_path: str
                輸出文件的路徑。

        Returns
            None
        """
        # check
        if not isinstance(output_path, str):
            raise TypeError("output_path必須是str。")
        output_path = os.path.abspath(output_path)
        if os.path.exists(os.path.dirname(output_path)) is False:
            raise ValueError("output_path的目錄不存在。")
        if not output_path.endswith(".tif"):
            raise ValueError("output_path必須是一個tif文件。")

        # write
        with rasterio.open(output_path, 'w', **self.meta) as dst:
            dst.write(self.data, 1)
