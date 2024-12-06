"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-07
Description: This module defines a map class for quickmap.
"""
from cartopy import crs as ccrs
import numpy as np
import json

from .Canvas import Canvas
from .CoastlineLayer import CoastlineLayer
from .ColorBar import ColorBar
from .ContourLayer import ContourLayer
from .CountriesBorderLayer import CountriesBorderLayer
from .GridLineLayer import GridLineLayer
from .LakesLayer import LakesLayer
from .Layer import Layer
from .LayerList import LayerList
from .Remark import Remark
from .RiversLayer import RiversLayer
from .ShadingLayer import ShadingLayer
from .SubTitle import SubTitle
from .Title import Title
from .utils import *


class MapDescription(object):
    """
    這是一個地圖描述文件的類，會建立詳細的地圖繪製資訊，後續可供地圖渲染器使用。

    Attributes
        - title: Title
            主標題。
        - subtitle: SubTitle
            副標題。
        - remark: Remark
            備註。
        - canvas: Canvas
            畫布。
        - layer_list: LayerList
            圖層列表。
        - layer_of_colorbar: ColorBar
            色條所表示的圖層。
        - colorbar: ColorBar
            色條。

    Class Methods
        - base_map(lon_range: list = [-180, 180], lat_range: list = [-90, 90]): 利用指定範圍繪製基圖（Base Map）。
        - a_shading_from_a_geotiff(geotiff_path: str, band: int = 1): 從一個geotiff文件創建一個塗色地圖。
        - a_contour_from_a_geotiff(geotiff_path: str, band: int = 1): 從一個geotiff文件創建一個等高線地圖。
        - contour_and_shading_from_two_geotiff(contour_geotiff_path: str, shading_geotiff_path: str, contour_band: int = 1, shading_band: int = 1): 從兩個geotiff文件創建一個等高線和塗色地圖。

    Static Methods
        - get_proper_grid(x_range: int|float = 360, y_range: int|float = 180, max_grid_line_count: int = 9): 根據畫布的範圍，獲取適合的經緯度網格。
        - get_proper_resolution(x_range: int|float = 360, y_range: int|float = 180): 根據畫布的範圍，獲取適合的Nature Earth解析度。

    Methods
        - export_to_json(json_path: str): 將地圖描述文件導出為json文件。
    """

    def __init__(self,
                 title: Title = None,
                 subtitle: SubTitle = None,
                 remark: Remark = None,
                 canvas: Canvas = None,
                 layer_list: LayerList = None,
                 layer_of_colorbar: ColorBar = None,
                 colorbar: ColorBar = None):
        """
        建立一個地圖描述文件。

        Args
            - title: Title
                主標題。
            - subtitle: SubTitle
                副標題。
            - remark: remark
                備註。
            - canvas: Canvas
                畫布。
            - layer_list: LayerList
                圖層列表。
            - layer_of_colorbar: ColorBar
                色條表示的圖層。
            - colorbar: ColorBar
                色條。
        """
        self.__title = None
        self.__subtitle = None
        self.__remark = None
        self.__canvas = None
        self.__layer_list = None
        self.__layer_of_colorbar = None
        self.__colorbar = None

        self.title = title
        self.subtitle = subtitle
        self.remark = remark
        self.canvas = canvas
        self.layer_list = layer_list
        self.layer_of_colorbar = layer_of_colorbar
        self.colorbar = colorbar

    @classmethod
    def base_map(cls, lon_range: list = [-180, 180], lat_range: list = [-90, 90]):
        """
        利用指定範圍繪製基圖（Base Map）。

        Args
            - lon_range: list
                經度範圍，格式為[lon_left, lon_right]，預設為[-180, 180]。
            - lat_range: list
                緯度範圍，格式為[lat_min, lat_max]，預設為[-90, 90]。

        Returns
            - map: Map
                一個基圖。
        """
        # check lon
        if not isinstance(lon_range, list):
            raise TypeError("lon_range必須是list。")
        if len(lon_range) != 2:
            raise ValueError("lon_range必須包含兩個數字。")
        check_lon(lon_range[0])
        check_lon(lon_range[1])
        lon_left = lon_range[0]
        lon_right = lon_range[1]
        if lon_left >= lon_right:
            lon_right += 360

        # check lat
        if not isinstance(lat_range, list):
            raise TypeError("lat_range必須是list。")
        if len(lat_range) != 2:
            raise ValueError("lat_range必須包含兩個數字。")
        check_lat(lat_range[0])
        check_lat(lat_range[1])
        lat_min = lat_range[0]
        lat_max = lat_range[1]

        # create layer list
        layer_list = LayerList()

        # create a title
        title = Title("Base Map")

        # create a subtitle
        subtitle = SubTitle("")

        # create a remark
        remark = Remark("")

        # create canvas
        display_projection_crs = cls.get_proper_projection_crs(lon_range, lat_range)
        canvas = Canvas(lon_left, lon_right, lat_min, lat_max, display_projection_crs=display_projection_crs)

        # create reference layer
        resolution = cls.get_proper_resolution(lon_right-lon_left, lat_max-lat_min)
        rivers_layer = RiversLayer(resolution)
        lakes_layer = LakesLayer(resolution)
        coastline_layer = CoastlineLayer(resolution)
        countries_border_layer = CountriesBorderLayer(resolution, face_color=(1, 1, 1, 0))

        # create grid line layer
        plot_at_lon, plot_at_lat = cls.get_proper_grid(lon_right-lon_left, lat_max-lat_min)
        grid_line_layer = GridLineLayer(plot_at_lat, plot_at_lon)

        # add layers to layer list
        layer_list.add(rivers_layer)
        layer_list.add(lakes_layer)
        layer_list.add(coastline_layer)
        layer_list.add(countries_border_layer)
        layer_list.add(grid_line_layer)

        # create a colorbar
        colorbar = ColorBar()

        # create a map
        map = cls(title=title,
                  subtitle=subtitle,
                  remark=remark,
                  canvas=canvas,
                  layer_list=layer_list,
                  colorbar=colorbar)

        return map

    @classmethod
    def a_shading_from_a_geotiff(cls, geotiff_path: str, band: int = 1):
        """
        從一個geotiff文件創建一個塗色地圖。

        Args
            - geotiff_path: str
                geotiff文件的路徑。
            - band: int
                geotiff文件的band。

        Returns
            - map: Map
                一個塗色地圖。
        """
        # check
        if not isinstance(geotiff_path, str):
            raise TypeError("geotiff_path必須是str。")
        geotiff_path = os.path.abspath(geotiff_path)
        check_file_exist(geotiff_path)
        if (not geotiff_path.lower().endswith(".tif")) and (not geotiff_path.lower().endswith(".tiff")):
            raise ValueError("geotiff_path必須是一個tif文件。")
        check_not_negative(band)

        # create layer list
        layer_list = LayerList()

        # create shading layer
        shading_layer = ShadingLayer(geotiff_path, band)

        # create a title
        basename = os.path.basename(geotiff_path)
        title = Title(f"Shading Map: {basename}")

        # create a subtitle
        subtitle = SubTitle(f"Band: {band}")

        # create a remark
        remark = Remark("")

        # create canvas
        x_left = shading_layer.west_bound
        x_right = shading_layer.east_bound
        y_bottom = shading_layer.south_bound
        y_top = shading_layer.north_bound
        display_projection_crs = cls.get_proper_projection_crs([x_left, x_right], [y_bottom, y_top])
        canvas = Canvas(x_left, x_right, y_bottom, y_top, display_projection_crs=display_projection_crs)
        x_range = canvas.total_x_range
        y_range = canvas.total_y_range

        # create reference layer
        resolution = cls.get_proper_resolution(x_range, y_range)
        rivers_layer = RiversLayer(resolution)
        lakes_layer = LakesLayer(resolution)
        coastline_layer = CoastlineLayer(resolution, face_color=(1, 1, 1, 0))
        countries_border_layer = CountriesBorderLayer(resolution, face_color=(1, 1, 1, 0))

        # create grid line layer
        plot_at_lon, plot_at_lat = cls.get_proper_grid(x_range, y_range)
        grid_line_layer = GridLineLayer(plot_at_lat, plot_at_lon)

        # add layers to layer list
        layer_list.add(shading_layer)
        layer_list.add(rivers_layer)
        layer_list.add(lakes_layer)
        layer_list.add(coastline_layer)
        layer_list.add(countries_border_layer)
        layer_list.add(grid_line_layer)

        # set colorbar layer
        layer_of_colorbar = layer_list.select_layers_by_class(ShadingLayer)[0]

        # create a colorbar
        colorbar = ColorBar()

        # create a map
        map = cls(title=title,
                  subtitle=subtitle,
                  remark=remark,
                  canvas=canvas,
                  layer_list=layer_list,
                  layer_of_colorbar=layer_of_colorbar,
                  colorbar=colorbar)

        return map

    @classmethod
    def a_contour_from_a_geotiff(cls, geotiff_path: str, band: int = 1):
        """
        從一個geotiff文件創建一個等高線地圖。

        Args
            - geotiff_path: str
                geotiff文件的路徑。
            - band: int
                geotiff文件的band。

        Returns
            - map: Map
                一個等高線地圖。
        """
        # check
        if not isinstance(geotiff_path, str):
            raise TypeError("geotiff_path必須是str。")
        geotiff_path = os.path.abspath(geotiff_path)
        check_file_exist(geotiff_path)
        if (not geotiff_path.lower().endswith(".tif")) and (not geotiff_path.lower().endswith(".tiff")):
            raise ValueError("geotiff_path必須是一個tif文件。")
        check_not_negative(band)

        # create layer list
        layer_list = LayerList()

        # create contour layer
        contour_layer = ContourLayer(geotiff_path, band)

        # create a title
        basename = os.path.basename(geotiff_path)
        title = Title(f"Contour Map: {basename}")

        # create a subtitle
        subtitle = SubTitle(f"Band: {band}")

        # create a remark
        remark = Remark("")

        # create canvas
        x_left = contour_layer.west_bound
        x_right = contour_layer.east_bound
        y_bottom = contour_layer.south_bound
        y_top = contour_layer.north_bound
        display_projection_crs = cls.get_proper_projection_crs([x_left, x_right], [y_bottom, y_top])
        canvas = Canvas(x_left, x_right, y_bottom, y_top, display_projection_crs=display_projection_crs)
        x_range = canvas.total_x_range
        y_range = canvas.total_y_range

        # create reference layer
        resolution = cls.get_proper_resolution(x_range, y_range)
        rivers_layer = RiversLayer(resolution)
        lakes_layer = LakesLayer(resolution)
        coastline_layer = CoastlineLayer(resolution, face_color=(1, 1, 1, 0))
        countries_border_layer = CountriesBorderLayer(resolution, face_color=(1, 1, 1, 0))

        # create grid line layer
        plot_at_lon, plot_at_lat = cls.get_proper_grid(x_range, y_range)
        grid_line_layer = GridLineLayer(plot_at_lat, plot_at_lon)

        # add layers to layer list
        layer_list.add(coastline_layer)
        layer_list.add(countries_border_layer)
        layer_list.add(rivers_layer)
        layer_list.add(lakes_layer)
        layer_list.add(contour_layer)
        layer_list.add(grid_line_layer)

        # create a map
        map = cls(title=title,
                  subtitle=subtitle,
                  remark=remark,
                  canvas=canvas,
                  layer_list=layer_list)

        return map

    @classmethod
    def contour_and_shading_from_two_geotiff(
            cls,
            contour_geotiff_path: str,
            shading_geotiff_path: str,
            contour_band: int = 1,
            shading_band: int = 1):
        """
        從兩個geotiff文件創建一個等高線和塗色地圖。

        Args
            - contour_geotiff_path: str
                等高線geotiff文件的路徑。
            - shading_geotiff_path: str
                塗色geotiff文件的路徑。
            - contour_band: int
                等高線geotiff文件的band。
            - shading_band: int
                塗色geotiff文件的band。

        Returns
            - map_description: MapDescription
                一個等高線和塗色地圖描述文件。
        """
        # check contour
        if not isinstance(contour_geotiff_path, str):
            raise TypeError("contour_geotiff_path必須是str。")
        contour_geotiff_path = os.path.abspath(contour_geotiff_path)
        check_file_exist(contour_geotiff_path)
        if (not contour_geotiff_path.lower().endswith(".tif")) and (not contour_geotiff_path.lower().endswith(".tiff")):
            raise ValueError("contour_geotiff_path必須是一個tif文件。")
        check_not_negative(contour_band)

        # check shading
        if not isinstance(shading_geotiff_path, str):
            raise TypeError("shading_geotiff_path必須是str。")
        shading_geotiff_path = os.path.abspath(shading_geotiff_path)
        check_file_exist(shading_geotiff_path)
        if (not shading_geotiff_path.lower().endswith(".tif")) and (not shading_geotiff_path.lower().endswith(".tiff")):
            raise ValueError("shading_geotiff_path必須是一個tif文件。")
        check_not_negative(shading_band)

        # create layer list
        layer_list = LayerList()

        # create contour layer
        contour_layer = ContourLayer(contour_geotiff_path, contour_band)

        # create shading layer
        shading_layer = ShadingLayer(shading_geotiff_path, shading_band)

        # create a title
        contour_basename = os.path.basename(contour_geotiff_path)
        shading_basename = os.path.basename(shading_geotiff_path)
        title = Title(f"Contour and Shading Map: {contour_basename}, {shading_basename}")

        # create a subtitle
        contour_subtitle = SubTitle(f"Contour Band: {contour_band}")
        shading_subtitle = SubTitle(f"Shading Band: {shading_band}")

        # create a remark
        remark = Remark("")

        # create canvas
        x_left = contour_layer.west_bound
        x_right = contour_layer.east_bound
        y_bottom = contour_layer.south_bound
        y_top = contour_layer.north_bound
        display_projection_crs = cls.get_proper_projection_crs([x_left, x_right], [y_bottom, y_top])
        canvas = Canvas(x_left, x_right, y_bottom, y_top, display_projection_crs=display_projection_crs)
        x_range = canvas.total_x_range
        y_range = canvas.total_y_range

        # create reference layer
        resolution = cls.get_proper_resolution(x_range, y_range)
        rivers_layer = RiversLayer(resolution)
        lakes_layer = LakesLayer(resolution)
        coastline_layer = CoastlineLayer(resolution, face_color=(1, 1, 1, 0))
        countries_border_layer = CountriesBorderLayer(resolution, face_color=(1, 1, 1, 0))

        # create grid line layer
        plot_at_lon, plot_at_lat = cls.get_proper_grid(x_range, y_range)
        grid_line_layer = GridLineLayer(plot_at_lat, plot_at_lon)

        # add layers to layer list
        layer_list.add(shading_layer)
        layer_list.add(rivers_layer)
        layer_list.add(lakes_layer)
        layer_list.add(coastline_layer)
        layer_list.add(countries_border_layer)
        layer_list.add(contour_layer)
        layer_list.add(grid_line_layer)

        # set colorbar layer
        layer_of_colorbar = layer_list.select_layers_by_class(ShadingLayer)[0]

        # create a colorbar
        colorbar = ColorBar()

        # create a map
        map_description = cls(title=title,
                              subtitle=contour_subtitle,
                              remark=remark,
                              canvas=canvas,
                              layer_list=layer_list,
                              layer_of_colorbar=layer_of_colorbar,
                              colorbar=colorbar)

        return map_description

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title: Title):
        if title is not None and not isinstance(title, Title):
            raise TypeError("title必須是Title或None，但輸入為{}。".format(type(title)))
        self.__title = title

    @property
    def subtitle(self):
        return self.__subtitle

    @subtitle.setter
    def subtitle(self, subtitle: SubTitle):
        if isinstance(subtitle, str):
            raise TypeError("subtitle必須是SubTitle或None，若要設置字串，請對SubTitle的.text_content屬性進行設置。")
        elif subtitle is not None and not isinstance(subtitle, SubTitle):
            raise TypeError("subtitle必須是SubTitle或None。")
        self.__subtitle = subtitle

    @property
    def remark(self):
        return self.__remark

    @remark.setter
    def remark(self, remark: Remark):
        if remark is not None and not isinstance(remark, Remark):
            raise TypeError("remark必須是remark或None。")
        self.__remark = remark

    @property
    def canvas(self):
        return self.__canvas

    @canvas.setter
    def canvas(self, canvas: Canvas):
        if canvas is not None and not isinstance(canvas, Canvas):
            raise TypeError("canvas必須是Canvas或None。")
        self.__canvas = canvas

    @property
    def layer_list(self):
        return self.__layer_list

    @layer_list.setter
    def layer_list(self, layer_list: LayerList):
        if (layer_list is not None) and (not isinstance(layer_list, LayerList)):
            raise TypeError("layer_list必須是LayerList或None。")
        self.__layer_list = layer_list

    @property
    def layer_of_colorbar(self):
        return self.__layer_of_colorbar

    @layer_of_colorbar.setter
    def layer_of_colorbar(self, layer_of_colorbar: Layer):
        if layer_of_colorbar is None:
            self.__layer_of_colorbar = None
            return

        current_layer_list = self.__layer_list.get_list()
        if layer_of_colorbar not in current_layer_list:
            raise ValueError("layer_of_colorbar必須在layer_list中。")

        self.__layer_of_colorbar = layer_of_colorbar

    @property
    def colorbar(self):
        return self.__colorbar

    @colorbar.setter
    def colorbar(self, colorbar: ColorBar):
        if colorbar is not None and not isinstance(colorbar, ColorBar):
            raise TypeError("colorbar必須是ColorBar或None。")
        self.__colorbar = colorbar

    @staticmethod
    def get_proper_grid(x_range: int | float = 360, y_range: int | float = 180, max_grid_line_count: int = 12) -> tuple[list[float], list[float]]:
        """
        根據畫布的範圍，獲取適合的經緯度網格。

        Args
            - x_range: int|float
                x軸的範圍。
            - y_range: int|float
                y軸的範圍。

        Returns
            - plot_at_lon: list[float]
                經度網格。
            - plot_at_lat: list[float]
                緯度網格。
        """
        # config
        recommend_grid_interval = [0.1, 0.2, 0.5, 1, 2, 5, 10, 15, 20, 25, 30]

        # check
        check_positive(x_range)
        check_positive(y_range)
        if not isinstance(max_grid_line_count, int):
            raise TypeError("max_grid_line必須是int。")
        check_positive(max_grid_line_count)

        # get proper grid
        for interval in recommend_grid_interval:
            if x_range / interval <= max_grid_line_count+1:
                x_interval = interval
                break
        for interval in recommend_grid_interval:
            if y_range / interval <= max_grid_line_count+1:
                y_interval = interval
                break

        # get proper interval
        interval = max(x_interval, y_interval)

        # create grid list
        x_grid_list = list(np.arange(-180, 180.00000000001, interval))
        x_grid_list = [float(i) for i in x_grid_list]
        y_grid_list = list(np.arange(-90, 90.00000000001, interval))
        y_grid_list = [float(i) for i in y_grid_list]

        return x_grid_list, y_grid_list

    @staticmethod
    def get_proper_resolution(x_range: int | float = 360, y_range: int | float = 180) -> str:
        """
        根據畫布的範圍，獲取適合的Nature Earth解析度。

        Args
            - x_range: int|float
                x軸的範圍。
            - y_range: int|float
                y軸的範圍。

        Returns
            - resolution: str
                Nature Earth解析度。
        """
        # check
        check_positive(x_range)
        check_positive(y_range)

        # get proper resolution
        if x_range >= 120 and y_range >= 120:
            resolution = "110m"
        elif x_range >= 60 and y_range >= 30:
            resolution = "50m"
        else:
            resolution = "10m"
        return resolution

    @staticmethod
    def get_proper_projection_crs(x_range: list, y_range: list) -> str:
        """
        根據畫布的範圍，獲取適合的投影座標系統。

        Args
            - x_range: list
                x軸的範圍。
            - y_range: list
                y軸的範圍。

        Returns
            - projection_crs: str
                建議的投影方式
        """
        # check
        if not isinstance(x_range, list):
            raise TypeError("x_range必須是list。")
        if len(x_range) != 2:
            raise ValueError("x_range必須包含兩個數字。")
        # check_lon(x_range[0])
        # check_lon(x_range[1])
        if x_range[0] >= x_range[1]:
            x_range[1] += 360

        if not isinstance(y_range, list):
            raise TypeError("y_range必須是list。")
        if len(y_range) != 2:
            raise ValueError("y_range必須包含兩個數字。")
        # check_lat(y_range[0])
        # check_lat(y_range[1])

        # get proper projection crs
        if y_range[0] > 80 or y_range[1] < -80:
            projection_crs = "polar_orthographic"
        elif y_range[0] > 30 or y_range[1] < -30:
            projection_crs = "lambert"
        else:
            projection_crs = "platecarree"

        return projection_crs

    def set_proper_grid(self, max_grid_line_count: int = 12):
        """
        設置適合的經緯度網格。
        """
        x_range = self.canvas.total_x_range
        y_range = self.canvas.total_y_range
        plot_at_lon, plot_at_lat = self.get_proper_grid(x_range, y_range, max_grid_line_count)
        for grid_line_layer in self.layer_list.select_layers_by_class(GridLineLayer):
            grid_line_layer.plot_at_lon = plot_at_lon
            grid_line_layer.plot_at_lat = plot_at_lat
        return

    def set_proper_resolution(self):
        """
        設置適合的Nature Earth解析度。
        """
        x_range = self.canvas.total_x_range
        y_range = self.canvas.total_y_range
        resolution = self.get_proper_resolution(x_range, y_range)
        for layer_type in [CoastlineLayer, CountriesBorderLayer, RiversLayer, LakesLayer]:
            for layer in self.layer_list.select_layers_by_class(layer_type):
                layer.resolution = resolution
        return

    def export_to_json_for_ncmapper(self, json_path: str | None = None, include_original_data: bool = True) -> str:
        """
        為ncmaper，將地圖描述文件導出為json文件。

        Args
            - json_path: str|None
                json文件的路徑，若為None，則只返回json字符串，預設為None。
            - include_original_data: bool
                是否將原始資料(陣列值)導出，預設為True。
        """
        # check
        if not isinstance(json_path, (str, type(None))):
            raise TypeError("json_path必須是str或None。")
        if json_path is not None:
            json_path = os.path.abspath(json_path)
            check_file_exist(json_path)
            if not json_path.lower().endswith(".json"):
                raise ValueError("json_path必須是一個json文件。")
        if not isinstance(include_original_data, bool):
            raise TypeError("include_original_data必須是bool。")

        # 產生字典資料
        map_description_dict = {
            "title": {
                "text_content": self.title.text_content,
                "font_size": self.title.font_size,
                "font_weight": self.title.font_weight,
                "font_color": self.title.font_color,
                "font": self.title.font,
            },
            "subtitle": {
                "text_content": self.title.text_content,
                "font_size": self.title.font_size,
                "font_weight": self.title.font_weight,
                "font_color": self.title.font_color,
                "font": self.title.font,
            },
            "remark": {
                "text_content": self.title.text_content,
                "font_size": self.title.font_size,
                "font_weight": self.title.font_weight,
                "font_color": self.title.font_color,
                "font": self.title.font,
            },
            "canvas": {
                "x_left": self.canvas.x_left,
                "x_right": self.canvas.x_right,
                "y_min": self.canvas.y_min,
                "y_max": self.canvas.y_max,
                "edge_color": self.canvas.edge_color,
                "edge_width": self.canvas.edge_width,
                "display_projection_crs": self.canvas.display_projection_crs.to_wkt(),
                "total_x_range": self.canvas.total_x_range,
                "total_y_range": self.canvas.total_y_range,
            },
            "colorbar": {
                "ticks_font_size": self.colorbar.ticks_font_size,
                "ticks_font_weight": self.colorbar.ticks_font_weight,
                "ticks_font_color": self.colorbar.ticks_font_color,
                "ticks_font": self.colorbar.ticks_font,
                "label_title_font_size": self.colorbar.label_title_font_size,
                "label_title_font_weight": self.colorbar.label_title_font_weight,
                "label_title_font_color": self.colorbar.label_title_font_color,
                "label_title_font": self.colorbar.label_title_font,
            },
            "shading_layer": {
                'data': self.layer_list.select_layers_by_class(ShadingLayer)[0].data.tolist(),
                'value_type': self.layer_list.select_layers_by_class(ShadingLayer)[0].value_type,
                'interpolation': self.layer_list.select_layers_by_class(ShadingLayer)[0].interpolation,
                'west_bound': self.layer_list.select_layers_by_class(ShadingLayer)[0].west_bound,
                'east_bound': self.layer_list.select_layers_by_class(ShadingLayer)[0].east_bound,
                'south_bound': self.layer_list.select_layers_by_class(ShadingLayer)[0].south_bound,
                'north_bound': self.layer_list.select_layers_by_class(ShadingLayer)[0].north_bound,
                'crs': ccrs.PlateCarree().to_wkt(),
                'value_color_dict': self.layer_list.select_layers_by_class(ShadingLayer)[0].value_color_dict,
                'is_visible': self.layer_list.select_layers_by_class(ShadingLayer)[0].is_visible,
            },
            "contour_layer": {
                'data': self.layer_list.select_layers_by_class(ContourLayer)[0].data.tolist(),
                'value_base': self.layer_list.select_layers_by_class(ContourLayer)[0].value_base,
                'value_interval': self.layer_list.select_layers_by_class(ContourLayer)[0].value_interval,
                'primary_contour_each': self.layer_list.select_layers_by_class(ContourLayer)[0].primary_contour_each,
                'line_color': self.layer_list.select_layers_by_class(ContourLayer)[0].line_color,
                'line_width': self.layer_list.select_layers_by_class(ContourLayer)[0].line_width,
                'west_bound': self.layer_list.select_layers_by_class(ContourLayer)[0].west_bound,
                'east_bound': self.layer_list.select_layers_by_class(ContourLayer)[0].east_bound,
                'south_bound': self.layer_list.select_layers_by_class(ContourLayer)[0].south_bound,
                'north_bound': self.layer_list.select_layers_by_class(ContourLayer)[0].north_bound,
                'crs': ccrs.PlateCarree().to_wkt(),
                "min_of_original_data": self.layer_list.select_layers_by_class(ContourLayer)[0].min_of_original_data,
                "max_of_original_data": self.layer_list.select_layers_by_class(ContourLayer)[0].max_of_original_data,
                'font_size': self.layer_list.select_layers_by_class(ContourLayer)[0].font_size,
                'font_color': self.layer_list.select_layers_by_class(ContourLayer)[0].font_color,
                'label_format': self.layer_list.select_layers_by_class(ContourLayer)[0].label_format,
                'is_visible': self.layer_list.select_layers_by_class(ContourLayer)[0].is_visible,
            },
            "grid_line_layer": {
                'plot_at_lat': self.layer_list.select_layers_by_class(GridLineLayer)[0].plot_at_lat,
                'plot_at_lon': self.layer_list.select_layers_by_class(GridLineLayer)[0].plot_at_lon,
                'line_color': self.layer_list.select_layers_by_class(GridLineLayer)[0].line_color,
                'line_width': self.layer_list.select_layers_by_class(GridLineLayer)[0].line_width,
                'label_size': self.layer_list.select_layers_by_class(GridLineLayer)[0].label_size,
                'label_color': self.layer_list.select_layers_by_class(GridLineLayer)[0].label_color,
                'label_weight': self.layer_list.select_layers_by_class(GridLineLayer)[0].label_weight,
                'label_font': self.layer_list.select_layers_by_class(GridLineLayer)[0].label_font,
                'is_visible': self.layer_list.select_layers_by_class(GridLineLayer)[0].is_visible,
            }
        }

        if not include_original_data:
            map_description_dict["shading_layer"]['data'] = None
            map_description_dict["contour_layer"]['data'] = None

        return json.dumps(map_description_dict, indent=4)
