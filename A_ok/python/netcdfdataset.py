import affine
import numpy as np
import os
import rasterio
from rasterio.transform import from_origin
import xarray as xr
from typing import Optional, Union


class NetCDFDataset(object):
    """
    自定的NetCDF資料物件，用於處理WGS1984(經緯度座標系統)的NetCDF檔案。

    Attributes:
        *Dataset*
        - dataset: xarray.Dataset
            NetCDF檔案的資料集

        *User-Input*
        - file_path: str
            NetCDF檔案的路徑
        - x_name: str
            在NetCDF檔案中代表東西（橫）軸的coordinate之名稱。
        - y_name: str
            在NetCDF檔案中代表南北（縱）軸的coordinate之名稱。
        - z_name: str|None
            在NetCDF檔案中代表高度的coordinate之名稱，若無該coordinate，則設為None。
        - time_name: str|None
            在NetCDF檔案中代表時間的coordinate之名稱，若無該coordinate，則設為None。

        *Other*
        - is_regional: bool
            是否為區域性的NetCDF檔案。
        - is_global: bool
            是否為全球性的NetCDF檔案。
        - x_list: list
            東西（橫）軸所有值的list。
        - y_list: list
            南北（縱）軸所有值的list。
        - z_list: list
            高度軸所有值的list。
        - time_list: list
            時間軸所有值的list。
        - variable_list: list
            所有變數名稱的list。
        - one_part: bool
            此NetCDF檔案是否為一個部分的資料。(nc檔的x軸沒有跨越180度經度，因此沒有被拆分為兩個部分)
        - two_parts: bool
            此NetCDF檔案是否為兩個部分的資料。(nc檔的x軸有跨越180度經度，因此被拆分為兩個部分)

        *Methods*
        - show_z_list_of_specific_variable(variable: str)->list
            顯示指定變數的高度軸的所有值。
        - inside(x: float, y: float)->bool
            判斷指定的經緯度是否在NetCDF檔案的範圍內。
        - select_to_xarray(variable: str, time: any, z: any, x_range: list|None=None, y_range: list|None=None, interpolation_to_equal_interval: bool=False)->xarray.DataArray
            選取指定的變數、時間、層面、緯度、經度的二維資料，並回傳該資料的xarray.DataArray。
        - select_to_ndarray(variable: str, time: any, z: any, x_range: list|None=None, y_range: list|None=None)->np.ndarray
            選取指定的變數、時間、層面、緯度、經度的二維資料，並回傳該資料的np.ndarray。
        - select_to_geotiff(save_at: str, variable: str, time: any, z: any, x_range: list|None=None, y_range: list|None=None)->None
            選取指定的變數、時間、層面、緯度、經度的二維資料，並將該資料存成GeoTiff檔案。
    """

    def __init__(self, file_path: str, x_name: str, y_name: str, z_name: Union[str, None], time_name: Union[str, None], *args, **kwargs) -> None:
        """
        建立一個 NetCDFDataset 物件。

        Args:
            file_path: str
                NetCDF檔案的路徑。
            x_name: str
                在NetCDF檔案中代表東西（橫）軸的coordinate之名稱。
            y_name: str
                在NetCDF檔案中代表南北（縱）軸的coordinate之名稱。
            z_name: str|None
                在NetCDF檔案中代表高度軸的coordinate之名稱，若無該coordinate則設為None。
            time_name: str|None
                在NetCDF檔案中代表時間軸的coordinate之名稱，若無該coordinate則設為None。

        Returns:
            None
        """
        # 檢查輸入的參數是否符合規定
        required_str_args = {'file_path': file_path, 'x_name': x_name, 'y_name': y_name}
        optional_str_args = {'z_name': z_name, 'time_name': time_name}

        for arg, value in required_str_args.items():
            if not isinstance(value, str):
                raise TypeError(f"{arg} must be a string.")

        for arg, value in optional_str_args.items():
            if not isinstance(value, (str, type(None))):
                raise TypeError(f"{arg} must be a string or None.")

        # 讀取NetCDF檔案
        self.dataset = xr.open_dataset(file_path, *args, **kwargs)

        # 檢查並取得坐標
        coordinates = {name: self.dataset.coords[name] for name in [x_name, y_name] if name in self.dataset.coords}
        if len(coordinates) < 2:
            raise ValueError("x_name and y_name must be present in dataset coordinates.")
        if z_name and z_name not in self.dataset.coords:
            raise ValueError(f"z_name '{z_name}' not found in dataset coordinates.")
        if time_name and time_name not in self.dataset.coords:
            raise ValueError(f"time_name '{time_name}' not found in dataset coordinates.")

        # 檢查x、y是否是數字
        for coord in [x_name, y_name]:
            if not np.issubdtype(self.dataset[coord].dtype, np.number):
                raise ValueError(f"{coord} coordinate must be a number.")

        # 判斷是否全球性檔案
        x_min, x_max = float(self.dataset[x_name].min()), float(self.dataset[x_name].max())
        x_resolution = float(self.dataset[x_name].diff(x_name).mean())
        x_range = round((x_max + x_resolution / 2) - (x_min - x_resolution / 2), 0)

        if x_range == 360:
            self.is_global = True
            self.is_regional = False
        elif 0 < x_range < 360:
            self.is_global = False
            self.is_regional = True
        else:
            raise ValueError("Can't parse the x coordinate, please check the x coordinate.")

        # 檢查Y軸範圍
        y_min, y_max = float(self.dataset[y_name].min()), float(self.dataset[y_name].max())
        y_resolution = float(self.dataset[y_name].diff(y_name).mean())
        y_range = round((y_max + y_resolution / 2) - (y_min - y_resolution / 2), 0)
        if y_range > 180:
            raise ValueError("The y coordinate range should not exceed 180 degrees.")

        # 重新設定並排序x的值
        self.dataset[x_name] = (self.dataset[x_name] - 180) % 360 - 180
        self.dataset = self.dataset.sortby(x_name)

        # 排序y的值
        self.dataset = self.dataset.sortby(y_name)

        # 設定屬性
        self.file_path = file_path
        self.x_name = x_name
        self.y_name = y_name
        self.z_name = z_name
        self.time_name = time_name

    def __getattr__(self, name):
        return getattr(self.dataset, name)

    @property
    def x_list(self) -> list:
        """
        列出東西（橫）軸的所有值，並以list形式回傳。

        Returns:
            list: 東西（橫）軸的所有值。
        """
        x_name = self.x_name
        x_values = self.dataset[x_name].values
        x_list = [np.float32(x_value) for x_value in x_values]
        return x_list

    @property
    def y_list(self) -> list:
        """
        回傳南北（縱）軸的所有值。

        Returns:
            list: 南北（縱）軸的所有值
        """
        y_name = self.y_name
        y_values = self.dataset[y_name].values
        y_list = [np.float32(y_value) for y_value in y_values]
        return y_list

    @property
    def z_list(self) -> list:
        """
        回傳高度軸的所有值。

        Returns:
            list: 高度軸的所有值
        """
        z_name = self.z_name
        if z_name is None:
            z_list = list()
        else:
            z_values = self.dataset[z_name].values
            z_list = list(z_values)
        return z_list

    @property
    def time_list(self) -> list:
        """
        回傳時間軸的所有值。

        Returns:
            list: 時間軸的所有值
        """
        time_name = self.time_name
        if time_name is None:
            time_list = list()
        else:
            time_values = self.dataset[time_name].values
            time_list = list(time_values)
        return time_list

    @property
    def variable_list(self) -> list:
        """
        回傳所有變數的名稱。

        Returns:
            list: 所有變數的名稱
        """
        variable_list = list(self.dataset.data_vars)
        return variable_list

    @property
    def one_part(self) -> bool:
        """
        判斷資料是否沒有橫跨經度180度的部分，導致有兩個部分的資料。

        Returns:
            bool: 是否為一個部分的資料
        """
        if self.x_list[0] > self.x_list[-1]:
            return True
        else:
            return False

    @property
    def two_parts(self) -> bool:
        """
        判斷資料是否有橫跨經度180度的部分，導致有兩個部分的資料。

        Returns:
            bool: 是否為兩個部分的資料
        """
        return not self.one_part

    def inside(self, x: float, y: float) -> bool:
        """
        判斷指定的經緯度是否在NetCDF檔案的範圍內。
        """
        # load data
        x_list = self.x_list
        y_list = self.y_list
        x_name = self.x_name
        y_name = self.y_name
        dataset = self.dataset

        # 判斷x是否有兩個部分（例如170~-170代表有170~180、-180~-170兩個部分）
        if x_list[1] > x_list[0]:
            one_part = False
            two_parts = True
        else:
            one_part = True
            two_parts = False

        if one_part:
            x_resolution = float(dataset[x_name].diff(x_name).mean())
            x_min = self.x_list[0] - x_resolution/2
            x_max = self.x_list[-1] + x_resolution/2
            y_resolution = float(dataset[y_name].diff(y_name).mean())
            y_min = self.y_list[0] - y_resolution/2
            y_max = self.y_list[-1] + y_resolution/2

            if x < x_min:
                return False
            if x > x_max:
                return False
            if y < y_min:
                return False
            if y > y_max:
                return False
            return True

        elif two_parts:
            # is in part 1?
            x_resolution = float(dataset[x_name].diff(x_name).mean())
            x_min = self.x_list[0] - x_resolution/2
            x_max = 180
            y_resolution = float(dataset[y_name].diff(y_name).mean())
            y_min = self.y_list[0] - y_resolution/2
            y_max = self.y_list[-1] + y_resolution/2

            if x < x_min:
                in_part_1 = False
            if x > x_max:
                in_part_1 = False
            if y < y_min:
                in_part_1 = False
            if y > y_max:
                in_part_1 = False
            in_part_1 = True

            # is in part 2?
            x_resolution = float(dataset[x_name].diff(x_name).mean())
            x_min = -180
            x_max = self.x_list[-1] + x_resolution/2
            y_resolution = float(dataset[y_name].diff(y_name).mean())
            y_min = self.y_list[0] - y_resolution/2
            y_max = self.y_list[-1] + y_resolution/2

            if x < x_min:
                in_part_2 = False
            if x > x_max:
                in_part_2 = False
            if y < y_min:
                in_part_2 = False
            if y > y_max:
                in_part_2 = False
            in_part_2 = True

            if in_part_1 or in_part_2:
                return True
            else:
                return False

    def show_z_list_of_specific_variable(self, variable: str) -> list:
        """
        顯示指定變數的高度軸的所有值。

        Args:
            variable (str): 要查看的變數名稱。

        Returns:
            list: 指定變數的高度軸的所有值。
        """
        # 檢查使用者輸入
        if not isinstance(variable, str):
            raise TypeError("`variable` must be a string.")
        if variable not in self.variable_list:
            variable_list = [str(variable) for variable in self.variable_list]
            variable = str(variable)
            error_msg = "Available variables are " + ", ".join(variable_list) + "but got" + variable + "."
            raise ValueError("`variable` should in variable_list." + error_msg)

        # 讀取高度軸的值
        z_name = self.z_name
        try:
            z_values = self.dataset[variable][z_name].values
            z_list = list(z_values)
        except KeyError:
            z_list = list()

        # 回傳高度軸的值
        for i in range(len(z_list)):
            z_list[i] = float(z_list[i])

        return z_list

    def __select(self,
                 variable: str,
                 time: any,
                 z: any,
                 x_range: Union[list, None] = None,
                 y_range: Union[list, None] = None,
                 interpolation_to_equal_interval: bool = False
                 ) -> tuple:
        """
        選取指定的變數、時間、層面、度、經度的二維資料，並回傳該資料的np.ndarray、xarray.DataArray、geotransform。

        Args:
            variable (str): 要挑選的變數名稱。
            time (any): 時間，請依據時間軸的資料型態輸入。若無時間軸，則設為None。
            z (any): 高度，請依據高度軸的資料型態輸入。若無高度軸，則設為None。
            x_range (list): 東西（橫）軸的範圍，輸入一個list，list[0]為起始值，list[1]為結束值，None代表不限制範圍。預設為None。
            y_range (list): 南北（縱）軸的範圍，輸入一個list，list[0]為起始值，list[1]為結束值，None代表不限制範圍。預設為None。
            interpolation_to_equal_interval (bool): 是否將x、y設為等間距，預設為False。

        Returns:
            tuple
                1. xarray.DataArray: 二維資料的xarray.DataArray。
                2. numpy.ndarray: 二維資料的np.ndarray。
                3. affine.Affine: geotransform。
        """
        # 讀取各屬性
        dataset = self.dataset
        variable_list = self.variable_list
        x_list = self.x_list
        y_list = self.y_list
        z_list = self.z_list
        time_list = self.time_list
        x_name = self.x_name
        y_name = self.y_name
        z_name = self.z_name
        have_z_coordinate = z_name is not None
        time_name = self.time_name
        have_time_coordinate = time_name is not None

        # 檢查使用者輸入
        if not isinstance(variable, str):
            raise TypeError("`variable` must be a string.")
        if not isinstance(x_range, list) and not x_range is None:
            raise TypeError("`x_range` must be a list.")
        if not isinstance(y_range, list) and not y_range is None:
            raise TypeError("`y_range` must be a list.")
        if variable not in variable_list:
            variable_list = [str(variable) for variable in variable_list]
            variable = str(variable)
            error_msg = "Available variables are " + ", ".join(variable_list) + "but got" + variable + "."
            raise ValueError("`variable` should in variable_list." + error_msg)
        # if have_time_coordinate and time is None:
        #     raise ValueError("`time` is required since the dataset has a time dimension.")
        # if have_time_coordinate and time not in time_list:
        #     time_list = [str(time) for time in time_list]
        #     time = str(time)
        #     error_msg = "Available time are " + ", ".join(time_list) + "but got" + time + "."
        #     raise ValueError("`time` should in time_list." + error_msg)
        # if have_z_coordinate and z is None:
        #     raise ValueError("`z` is required since the dataset has a z dimension.")
        # if have_z_coordinate and z not in z_list:
        #     z_list = [str(z) for z in z_list]
        #     z = str(z)
        #     error_msg = "Available z are " + ", ".join(z_list) + "but got" + z + "."
        #     raise ValueError("`z` should in z_list." + error_msg)
        if x_range is not None:
            if len(x_range) != 2:
                raise ValueError("`x_range` should be a list with 2 elements, but got " + str(x_range) + ".")
            if x_range[0] > 180 or x_range[0] < -180 or x_range[1] > 180 or x_range[1] < -180:
                raise ValueError("`x_range` should >=-180 and <=180, but got " + str(x_range) + ".")
        if y_range is not None:
            if len(y_range) != 2:
                raise ValueError("`y_range` should be a list with 2 elements, but got " + str(y_range) + ".")
            if y_range[0] > 90 or y_range[0] < -90 or y_range[1] > 90 or y_range[1] < -90:
                raise ValueError("`y_range` should >=-90 and <=90, but got " + str(y_range) + ".")
            if y_range[0] > y_range[1]:
                raise ValueError("`y_range[0]` should <= `y_range[1]`.")

        # 調整x_range、y_range
        # 1. 無則選取全部
        # 2. 若x選到180度，則調整為179.99999999
        if x_range == None:
            x_range = [x_list[0], x_list[-1]]
        if y_range == None:
            y_range = [y_list[0], y_list[-1]]
        if x_range[0] == 180:
            x_range[0] = 179.99999999
        if x_range[1] == 180:
            x_range[1] = 179.99999999

        # 切出指定y範圍、時間、層面的變數
        result = dataset
        result = result[variable]
        result = result.sel({y_name: slice(y_range[0], y_range[1])})
        if have_time_coordinate and time is not None:
            result = result.sel({time_name: time})
        if have_z_coordinate and z is not None:
            result = result.sel({z_name: z})

        # 切出指定x範圍
        # 1. 判斷要選取 1個部分 or 2個部分 (如果橫跨180度經度就需要選取兩個部分)
        if x_range[0] > x_range[1]:
            select_one_part = False
            select_two_parts = True
        elif x_range[0] < x_range[1]:
            select_one_part = True
            select_two_parts = False
        # 2. 判斷要裁切的x範圍
        if select_one_part:
            result = result.sel({x_name: slice(x_range[0], x_range[1])})
        elif select_two_parts:
            result_part_1 = result.sel({x_name: slice(x_range[0], 179.99999999)})
            result_part_2 = result.sel({x_name: slice(-180, x_range[1])})

        # 如果切出來的資料大於2維，則只保留x、y兩個維度，並且其他維度只保留第一個
        coordinate_num = len(result.dims)
        if coordinate_num > 2:
            coordinate_name_list = list(result.dims)
            coordinate_name_list.delete(x_name)
            coordinate_name_list.delete(y_name)
            for coordinate_name in coordinate_name_list:
                Warning("There are more than 2 dimensions in the dataset, only kept " + coordinate_name + ":" + str(result[coordinate_name].values[0]) + ".")
                result.sel({coordinate_name: result[coordinate_name].values[0]}, drop=True)

        # 將x、y要為等間距，使用線性內差
        if interpolation_to_equal_interval and select_one_part:
            # 進行內差
            x_first = result[x_name].values[0]
            x_last = result[x_name].values[-1]
            y_first = result[y_name].values[0]
            y_last = result[y_name].values[-1]
            x = np.linspace(x_first, x_last, len(result[x_name]))
            y = np.linspace(y_first, y_last, len(result[y_name]))
            result = result.interp({x_name: x, y_name: y}, method='linear')
        elif interpolation_to_equal_interval and select_two_parts:
            # 內差第一部分
            part_1_x_first = result_part_1[x_name].values[0]
            part_1_x_last = result_part_1[x_name].values[-1]
            part_1_y_first = result_part_1[y_name].values[0]
            part_1_y_last = result_part_1[y_name].values[-1]
            part_1_x = np.linspace(part_1_x_first, part_1_x_last, len(result_part_1[x_name]))
            part_1_y = np.linspace(part_1_y_first, part_1_y_last, len(result_part_1[y_name]))
            result_part_1 = result_part_1.interp({x_name: part_1_x, y_name: part_1_y}, method='linear')
            # 內差第二部分
            part_2_x_first = result_part_2[x_name].values[0]
            part_2_x_last = result_part_2[x_name].values[-1]
            part_2_y_first = result_part_2[y_name].values[0]
            part_2_y_last = result_part_2[y_name].values[-1]
            part_2_x = np.linspace(part_2_x_first, part_2_x_last, len(result_part_2[x_name]))
            part_2_y = np.linspace(part_2_y_first, part_2_y_last, len(result_part_2[y_name]))
            result_part_2 = result_part_2.interp({x_name: part_2_x, y_name: part_2_y}, method='linear')

        # 若有兩個部分，則合併
        if select_two_parts:
            result_part_2[x_name] = result_part_2[x_name] + 360
            result = xr.concat([result_part_1, result_part_2], dim=x_name)

        # 將xarray.DataArray轉換成numpy.ndarray(2D)
        ndarray = result.values
        latitudes = result.coords[y_name].values
        if latitudes[0] < latitudes[-1]:
            ndarray = np.flipud(ndarray)
        longitudes = result.coords[x_name].values
        if longitudes[0] > longitudes[-1]:
            ndarray = np.fliplr(ndarray)

        # 取得geotransform
        x_resolution = abs(float(result[x_name].diff(x_name).mean()))
        y_resolution = abs(float(result[y_name].diff(y_name).mean()))
        x_origin = min(result[x_name].values) - x_resolution/2
        y_origin = max(result[y_name].values) + y_resolution/2
        geotransform = from_origin(x_origin, y_origin, x_resolution, y_resolution)

        return result, ndarray, geotransform

    def select_to_xarray(self, variable: str, time: any, z: any, x_range: Union[list, None] = None, y_range: Union[list, None] = None, interpolation_to_equal_interval: bool = False) -> xr.DataArray:
        """
        選取指定的變數、時間、層面、緯度、經度的二維資料，並回傳該資料的xarray.DataArray。

        Args:
            variable (str): 要挑選的變數名稱。
            time (any): 時間，請依據時間軸的資料型態輸入。
            z (any): 高度，請依據高度軸的資料型態輸入。
            x_range (list): 東西（橫）軸的範圍，輸入一個list，list[0]為起始值，list[1]為結束值，None代表不限制範圍。預設為None。
            y_range (list): 南北（縱）軸的範圍，輸入一個list，list[0]為起始值，list[1]為結束值，None代表不限制範圍。預設為None。
            interpolation_to_equal_interval (bool): 是否將x、y設為等間距，預設為False。

        Returns:
            xarray.DataArray: 二維資料的xarray.DataArray。
        """
        result, _, _ = self.__select(variable, time, z, x_range, y_range, interpolation_to_equal_interval)
        return result

    def select_to_ndarray(self, variable: str, time: any, z: any, x_range: Union[list, None] = None, y_range: Union[list, None] = None) -> np.ndarray:
        """
        選取指定的變數、時間、層面、緯度、經度的二維資料，並回傳該資料的np.ndarray。

        Args:
            variable (str): 要挑選的變數名稱。
            time (any): 時間，請依據時間軸的資料型態輸入。
            z (any): 高度，請依據高度軸的資料型態輸入。
            x_range (list): 東西（橫）軸的範圍，輸入一個list，list[0]為起始值，list[1]為結束值，None代表不限制範圍。預設為None。
            y_range (list): 南北（縱）軸的範圍，輸入一個list，list[0]為起始值，list[1]為結束值，None代表不限制範圍。預設為None。

        Returns:
            np.ndarray: 二維資料的np.ndarray。
        """
        _, ndarray, _ = self.__select(variable, time, z, x_range, y_range, interpolation_to_equal_interval=True)
        return ndarray

    def select_to_geotiff(self,
                          save_at: str,
                          variable: str,
                          time: any,
                          z: any,
                          x_range: Union[list, None] = None,
                          y_range: Union[list, None] = None,
                          ) -> None:
        """
        選取指定的變數、時間、層面、緯度、經度的二維資料，並將該資料存成GeoTiff檔案。

        Args:
            save_at (str): 要存檔的路徑。
            variable (str): 要挑選的變數名稱。
            time (any): 時間，請依據時間軸的資料型態輸入。
            z (any): 高度，請依據高度軸的資料型態輸入。
            x_range (list): 東西（橫）軸的範圍，輸入一個list，list[0]為起始值，list[1]為結束值，None代表不限制範圍。預設為None。
            y_range (list): 南北（縱）軸的範圍，輸入一個list，list[0]為起始值，list[1]為結束值，None代表不限制範圍。預設為None。

        Returns:
            None
        """
        _, nparray_data, geotransform = self.__select(variable, time, z, x_range, y_range, interpolation_to_equal_interval=True)

        # check user input
        # file extension should be .tif or .tiff
        save_at = os.path.abspath(save_at)
        if (not save_at.lower().endswith(".tif")) and \
           (not save_at.lower().endswith(".tiff")):
            raise ValueError("The file extension must be .tif or .tiff.")
        # file directory should exist
        file_dir = os.path.dirname(save_at)
        if not os.path.isdir(file_dir):
            raise FileNotFoundError("The directory of the file does not exist.")

        # create geotiff metadata
        metadata = {
            "driver": "GTiff",
            "count": 1,
            "dtype": np.float32,
            "width": nparray_data.shape[1],
            "height": nparray_data.shape[0],
            "crs": rasterio.crs.CRS.from_epsg(4326),
            "transform": geotransform,
            "nodata": np.nan
        }

        # write geotiff
        with rasterio.open(save_at, "w", **metadata) as dst:
            dst.write(nparray_data, 1)

        return None
