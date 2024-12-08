"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-07
Description: This module defines a coastline layer class for quickmap.
"""
from .Layer import Layer

from .utils import *


class CoastlineLayer(Layer):
    """
    地圖的海岸線圖層。
    """

    def __init__(self, resolution='10m', line_color='#1E1E1E', line_width=0.5, face_color=(0, 0, 0, 0), is_visible=True):
        """
        建立一個海岸線圖層。

        Args
            - resolution: 地圖的解析度，預設為"10m"。
            - line_color: 海岸線的顏色，預設為灰。
            - line_width: 海岸線的寬度（pixel），預設為 0.5。
            - face_color: 海岸線的填充顏色，預設為透明。
            - is_visible: 圖層是否顯示，預設為 True。
        """
        # check the input
        super().__init__(is_visible)
        self.__resolution = None
        self.__line_color = None
        self.__line_width = None
        self.__face_color = None

        self.resolution = resolution
        self.line_color = line_color
        self.line_width = line_width
        self.face_color = face_color

    @property
    def resolution(self):
        return self.__resolution

    @resolution.setter
    def resolution(self, resolution: str):
        check_nature_earth_resolution(resolution)
        self.__resolution = resolution

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
    def face_color(self):
        return self.__face_color

    @face_color.setter
    def face_color(self, face_color: str):
        face_color = check_and_convert_color(face_color)
        self.__face_color = face_color
