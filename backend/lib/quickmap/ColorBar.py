"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-07
Description: This module defines a colorbar class for quickmap.
"""
from .utils import *


class ColorBar(object):
    """
    以塗色表示的網格圖層的色條，此物件包含色條的字體資訊。

    Attributes
        - height_fraction: 色條的高度佔整個圖層的比例。
        - ticks_font_size: 色條標籤的字體大小。
        - ticks_font_weight: 色條標籤的字體粗細。
        - ticks_font_color: 色條標籤的字體顏色。
        - ticks_font: 色條標籤的字體，預設為Noto-TC。
        - label_title_font_size: 色條的標題字體大小。
        - label_title_font_weight: 色條的標題字體粗細。
        - label_title_font_color: 色條的標題字體顏色。
        - label_title_font: 色條的標題字體，預設為Noto-TC。
    """

    def __init__(self,
                 height_fraction: float = 2/7,
                 ticks_font_size: int = 12,
                 ticks_font_weight: int = 300,
                 ticks_font_color: str = '#1E1E1E',
                 ticks_font: str = 'Noto-TC',
                 label_title_font_size: int = 12,
                 label_title_font_weight: int = 400,
                 label_title_font_color: str = '#1E1E1E',
                 label_title_font: str = 'Noto-TC'):
        # init
        self.__height_fraction = None
        self.__ticks_font_size = None
        self.__ticks_font_weight = None
        self.__ticks_font_color = None
        self.__ticks_font = None
        self.__label_title_font_size = None
        self.__label_title_font_weight = None
        self.__label_title_font_color = None
        self.__label_title_font = None

        # set attributes
        self.height_fraction = height_fraction
        self.ticks_font_size = ticks_font_size
        self.ticks_font_weight = ticks_font_weight
        self.ticks_font_color = ticks_font_color
        self.ticks_font = ticks_font
        self.label_title_font_size = label_title_font_size
        self.label_title_font_weight = label_title_font_weight
        self.label_title_font_color = label_title_font_color
        self.label_title_font = label_title_font

    @property
    def height_fraction(self):
        return self.__height_fraction

    @height_fraction.setter
    def height_fraction(self, height_fraction: float):
        if not isinstance(height_fraction, float):
            raise TypeError("height_fraction必須是float。")
        if not 0 < height_fraction < 1:
            raise ValueError("height_fraction必須在0和1之間。")
        self.__height_fraction = height_fraction

    @property
    def ticks_font_size(self):
        return self.__ticks_font_size

    @ticks_font_size.setter
    def ticks_font_size(self, ticks_font_size: int):
        if not isinstance(ticks_font_size, int):
            raise TypeError("ticks_font_size必須是int。")
        check_positive(ticks_font_size)
        self.__ticks_font_size = ticks_font_size

    @property
    def ticks_font_weight(self):
        return self.__ticks_font_weight

    @ticks_font_weight.setter
    def ticks_font_weight(self, ticks_font_weight: int):
        if not isinstance(ticks_font_weight, int):
            raise TypeError("ticks_font_weight必須是int。")
        check_positive(ticks_font_weight)
        self.__ticks_font_weight = ticks_font_weight

    @property
    def ticks_font_color(self):
        return self.__ticks_font_color

    @ticks_font_color.setter
    def ticks_font_color(self, ticks_font_color: str):
        if not isinstance(ticks_font_color, str):
            raise TypeError("ticks_font_color必須是str。")
        ticks_font_color = check_and_convert_color(ticks_font_color)
        self.__ticks_font_color = ticks_font_color

    @property
    def ticks_font(self):
        return self.__ticks_font

    @ticks_font.setter
    def ticks_font(self, ticks_font: str):
        if not isinstance(ticks_font, str):
            raise TypeError("ticks_font必須是str。")
        self.__ticks_font = ticks_font

    @property
    def label_title_font_size(self):
        return self.__label_title_font_size

    @label_title_font_size.setter
    def label_title_font_size(self, label_title_font_size: int):
        if not isinstance(label_title_font_size, int):
            raise TypeError("label_title_font_size必須是int。")
        check_positive(label_title_font_size)
        self.__label_title_font_size = label_title_font_size

    @property
    def label_title_font_weight(self):
        return self.__label_title_font_weight

    @label_title_font_weight.setter
    def label_title_font_weight(self, label_title_font_weight: int):
        if not isinstance(label_title_font_weight, int):
            raise TypeError("label_title_font_weight必須是int。")
        check_positive(label_title_font_weight)
        self.__label_title_font_weight = label_title_font_weight

    @property
    def label_title_font_color(self):
        return self.__label_title_font_color

    @label_title_font_color.setter
    def label_title_font_color(self, label_title_font_color: str):
        if not isinstance(label_title_font_color, str):
            raise TypeError("label_title_font_color必須是str。")
        label_title_font_color = check_and_convert_color(label_title_font_color)
        self.__label_title_font_color = label_title_font_color

    @property
    def label_title_font(self):
        return self.__label_title_font

    @label_title_font.setter
    def label_title_font(self, label_title_font: str):
        if not isinstance(label_title_font, str):
            raise TypeError("label_title_font必須是str。")
        self.__label_title_font = label_title_font
