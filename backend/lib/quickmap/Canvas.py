"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-06
Description: This module defines a Canvas class for quickmap.
"""
from cartopy import crs as ccrs

from .utils import *


class Canvas(object):
    """
    地圖的主要繪圖區。

    Attributes
        - x_left (float): 地圖的左側經度，介於 -180.0 和 180.0 之間。
        - x_right (float): 地圖的最小經度，介於 -180.0 和 180.0 之間。
        - y_min (float): 地圖的最小緯度，介於 -90.0 和 90.0 之間，且小於 y_max。
        - y_max (float): 地圖的最大緯度，介於 -90.0 和 90.0 之間，且大於 y_min。
        - edge_color (str): 地圖邊界的顏色。
        - edge_width (float): 地圖邊界的寬度。
        - display_projection_crs (str or ccrs.Projection): 地圖的投影方式，cartopy.crs.Projection 物件。
        - ignore_warning (bool): 是否忽略警告。

    Properties
        - total_y_range (float): 地圖的總緯度範圍。
        - total_x_range (float): 地圖的總經度範圍。

    Class Attributes
        - supported_default_projection (list): 支援的預設投影方式。
        - acceptable_projection (tuple): 可接受的投影方式。
    """
    # config
    supported_default_projection = ["platecarree",
                                    "mercator",
                                    "lambert",
                                    "polar_orthographic"]
    acceptable_projection = (ccrs.PlateCarree,
                             ccrs.Mercator,
                             ccrs.LambertConformal,
                             ccrs.Orthographic)

    def __init__(self,
                 x_left: Union[int, float] = -180,
                 x_right: Union[int, float] = 180,
                 y_min: Union[int, float] = 90,
                 y_max: Union[int, float] = -90,
                 edge_color: str = "#1E1E1E",
                 edge_width: float = 0.8,
                 display_projection_crs: Union[str, ccrs.Projection] = "platecarree",
                 ignore_warning: bool = False):
        """
        初始化地圖的繪圖區。

        Args
            - x_left (int or float)
                地圖的左側經度，必須大於等於 -180 和小於 180 。預設為 -180。
            - x_right (int or float)
                地圖的最小經度，必須大於等於 -180 和小於 180 。預設為 180。
            - y_min (int or float)
                地圖的最小緯度，必須介於 -90 和 90 之間，且小於 y_max。預設為 -90。
            - y_max (int or float)
                地圖的最大緯度，必須介於 -90 和 90 之間，且大於 y_min。預設為 90。
            - edge_color (str)
                地圖邊界的顏色。預設為 "#1E1E1E"。
            - edge_width (float)
                地圖邊界的寬度。預設為 0.8。
            - display_projection_crs (str or ccrs.Projection)
                地圖的投影方式，可以是字串或是 cartopy.crs.Projection 物件(不建議，且限制必須是字串選項中的其中一種)。若要以字串輸入，可以是 "platecarree"、"mercator"、"lambert"、"polar_orthographic"。預設為 "platecarree"。
            - ignore_warning (bool)
                是否忽略警告，預設為 False。
        """
        # init (先初始化所有屬性，但令其為 None，不然在檢查屬性時可能會因為屬性不存在而出錯)
        self.__x_left = None
        self.__x_right = None
        self.__y_min = None
        self.__y_max = None
        self.__edge_color = None
        self.__edge_width = None
        self.__display_projection_crs = None
        self.__ignore_warning = None

        # set attributes
        self.x_left = x_left
        self.x_right = x_right
        self.y_max = y_max
        self.y_min = y_min
        self.edge_color = edge_color
        self.edge_width = edge_width
        self.display_projection_crs = display_projection_crs
        self.ignore_warning = ignore_warning

    @property
    def x_left(self):
        return self.__x_left

    @x_left.setter
    def x_left(self, x_left: Union[int, float]):
        # 是int或float
        if not isinstance(x_left, (int, float)):
            raise TypeError("x_left must be an integer or a float.")

        # 介於-180和180之間
        if x_left < -180 and x_left > 180:
            raise ValueError("x_left must be between -180 and 180.")

        # 轉換180度為179.9999
        if x_left == 180:
            x_left = 179.9999

        self.__x_left = float(x_left)

    @property
    def x_right(self):
        return self.__x_right

    @x_right.setter
    def x_right(self, x_right: Union[int, float]):
        # 是int或float
        if not isinstance(x_right, (int, float)):
            raise TypeError("x_right must be an integer or a float.")

        # 介於-180和180之間
        if x_right < -180 and x_right > 180:
            raise ValueError("x_right must be between -180 and 180.")

        # 轉換180度為179.9999
        if x_right == 180:
            x_right = 179.9999

        self.__x_right = float(x_right)

    @property
    def y_max(self):
        return self.__y_max

    @y_max.setter
    def y_max(self, y_max: Union[int, float]):
        # 是int或float
        if not isinstance(y_max, (int, float)):
            raise TypeError("y_max must be an integer or a float.")

        # 介於-90和90之間
        if y_max < -90 and y_max > 90:
            raise ValueError("y_max must be between -90 and 90.")

        # 大於y_min
        if self.y_min is not None and self.y_min >= y_max:
            raise ValueError("y_max must be greater than y_min.")

        self.__y_max = float(y_max)

    @property
    def y_min(self):
        return self.__y_min

    @y_min.setter
    def y_min(self, y_min: Union[int, float]):
        # 是int或float
        if not isinstance(y_min, (int, float)):
            raise TypeError("y_min must be an integer or a float.")

        # 介於-90和90之間
        if y_min < -90 and y_min > 90:
            raise ValueError("y_min must be between -90 and 90.")

        # 小於y_max
        if self.y_max is not None and y_min >= self.y_max:
            raise ValueError("y_min must be less than y_max.")

        self.__y_min = float(y_min)

    @property
    def edge_color(self):
        return self.__edge_color

    @edge_color.setter
    def edge_color(self, edge_color: str):
        if not isinstance(edge_color, str):
            raise TypeError("edge_color must be a string.")
        edge_color = check_and_convert_color(edge_color)
        self.__edge_color = edge_color

    @property
    def edge_width(self):
        return self.__edge_width

    @edge_width.setter
    def edge_width(self, edge_width: float):
        if not isinstance(edge_width, (int, float)):
            raise TypeError("edge_width must be an integer or a float.")
        edge_width = float(edge_width)
        check_positive(edge_width)
        self.__edge_width = edge_width

    @property
    def display_projection_crs(self):
        return self.__display_projection_crs

    @display_projection_crs.setter
    def display_projection_crs(self, display_projection_crs: Union[str, ccrs.Projection]):
        # if is string, check if it is supported
        if isinstance(display_projection_crs, str):
            if display_projection_crs not in self.supported_default_projection:
                raise ValueError("display_projection_crs not supported.")
            self.__display_projection_crs = self._default_projection(display_projection_crs)
        # if is cartopy.crs.Projection, check if it is acceptable
        elif isinstance(display_projection_crs, self.acceptable_projection):
            self.warn_crs_info()
            self.__display_projection_crs = display_projection_crs
        # else, raise error
        else:
            raise TypeError("display_projection_crs must be a string or a suppoted cartopy.crs.Projection object.")

    @property
    def ignore_warning(self):
        return self.__ignore_warning

    @ignore_warning.setter
    def ignore_warning(self, ignore_warning: bool):
        if not isinstance(ignore_warning, bool):
            raise TypeError("ignore_warning must be a boolean.")
        self.__ignore_warning = ignore_warning

    @property
    def total_y_range(self) -> float:
        """
        計算地圖的總緯度範圍。

        Returns
            - total_y_range (float)
                地圖的總緯度範圍。
        """
        return self.y_max - self.y_min

    @property
    def total_x_range(self) -> float:
        """
        計算地圖的總經度範圍。

        Returns
            - total_x_range (float)
                地圖的總經度範圍。
        """
        while self.x_right < self.x_left:
            self.x_right += 360
        return self.x_right - self.x_left

    def _default_projection(self, display_projection_crs: str):
        """
        根據使用者輸入的字串，自動計算此繪圖範圍下應使用的地圖投影參數，並回傳該投影物件。

        Args
            - display_projection_crs (str)
                地圖投影方式的字串，可以是 "platecarree"、"mercator"、"lambert"、"polar_orthographic"。

        Returns
            - proj_coor_sys (ccrs.Projection)
                地圖投影物件。
        """
        if display_projection_crs == "platecarree":
            return self._default_platecarree()
        elif display_projection_crs == "mercator":
            return self._default_mercator()
        elif display_projection_crs == "lambert":
            return self._default_lambert()
        elif display_projection_crs == "polar_orthographic":
            return self._default_polar_orthographic()
        else:
            raise ValueError("display_projection_crs not supported.")

    def _default_platecarree(self) -> ccrs.Projection:
        """
        自動計算此繪圖範圍下應使用的簡易圓柱地圖投影參數，並回傳該投影物件。

        Returns
            - proj_coor_sys (ccrs.Projection)
                簡易圓柱地圖投影物件。
        """
        # 以廣義角換算右側經度
        while self.x_right < self.x_left:
            self.x_right += 360

        # 計算中心經度
        central_longitude = (self.x_left + self.x_right) / 2

        # 將中心經度限制在 -180 和 180 之間
        while central_longitude >= 180:
            central_longitude -= 360
        while central_longitude < -180:
            central_longitude += 360

        proj_coor_sys = ccrs.PlateCarree(central_longitude=central_longitude)
        return proj_coor_sys

    def _default_mercator(self) -> ccrs.Projection:
        """
        自動計算此繪圖範圍下應使用的麥卡托圓柱地圖投影參數，並回傳該投影物件。

        Returns
            - proj_coor_sys (ccrs.Projection)
                麥卡托圓柱地圖投影物件。
        """
        # 以廣義角換算右側經度
        while self.x_right < self.x_left:
            self.x_right += 360

        # 計算中心經度
        central_longitude = (self.x_left + self.x_right) / 2

        # 將中心經度限制在 -180 和 180 之間
        while central_longitude > 180:
            central_longitude -= 360
        while central_longitude < -180:
            central_longitude += 360

        # 設定緯度
        max_latitude = self.y_max if self.y_max < 79 else 79
        min_latitude = self.y_min if self.y_min > -79 else -79

        proj_coor_sys = ccrs.Mercator(central_longitude=central_longitude, min_latitude=min_latitude, max_latitude=max_latitude)
        return proj_coor_sys

    def _default_lambert(self) -> ccrs.Projection:
        """
        自動計算此繪圖範圍下應使用的蘭伯特圓錐地圖投影參數，並回傳該投影物件。

        Returns
            - proj_coor_sys (ccrs.Projection)
                蘭伯特圓錐地圖投影物件。
        """
        # 以廣義角換算右側經度
        while self.x_right < self.x_left:
            self.x_right += 360

        # 計算中心經度
        central_longitude = (self.x_left + self.x_right) / 2

        # 將中心經度限制在 -180 和 180 之間
        while central_longitude > 180:
            central_longitude -= 360
        while central_longitude < -180:
            central_longitude += 360

        # 計算中心緯度
        central_latitude = (self.y_min + self.y_max) / 2

        # 標準緯度
        std_parallels_1 = self.y_min + (self.y_max - self.y_min) * (1/3)
        std_parallels_2 = self.y_min + (self.y_max - self.y_min) * (2/3)
        std_parallels = (std_parallels_1, std_parallels_2)
        proj_coor_sys = ccrs.LambertConformal(central_longitude=central_longitude,
                                              central_latitude=central_latitude,
                                              standard_parallels=std_parallels,
                                              cutoff=-80 if central_latitude >= 0 else 80)

        return proj_coor_sys

    def _default_polar_orthographic(self) -> ccrs.Projection:
        """
        自動計算此繪圖範圍下應使用的極平面正射投影參數，並回傳該投影物件。只能設定北極為中心的北半球範圍或南極為中心的南半球範圍。

        Returns
            - proj_coor_sys (ccrs.Projection)
                極平面正射投影物件。
        """
        # 計算中心經度
        central_longitude = (self.x_left + self.x_right) / 2

        # 將中心經度限制在 -180 和 180 之間
        while central_longitude > 180:
            central_longitude -= 360
        while central_longitude < -180:
            central_longitude += 360

        # 計算中心緯度
        extent_center_latitude = (self.y_min + self.y_max) / 2
        main_hemisphere = "north" if extent_center_latitude >= 0 else "south"
        central_latitude = 90 if main_hemisphere == "north" else -90

        # 設定投影方式
        proj_coor_sys = ccrs.Orthographic(central_longitude=central_longitude, central_latitude=central_latitude)
        return proj_coor_sys

    def warn_crs_info(self):
        """
        若使用者輸入自定義的地圖投影方式，則提供警告訊息。
        """
        if not self.ignore_warning:
            print("\033[33mWarning: Suggestions for display_projection_crs are following strings instead of self-defined projection, 'platecarree', 'mercator', 'lambert', 'polar_orthographic', self-defined Projection object is not recommended.\033[0m")

    def __str__(self):
        return f"Canvas(x_left={self.x_left}, x_right={self.x_right}, y_min={self.y_min}, y_max={self.y_max}, display_projection_crs={self.display_projection_crs})"

    def __repr__(self):
        return self.__str__()
