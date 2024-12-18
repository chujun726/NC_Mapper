"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-07
Description: This module defines a text class for quickmap.
"""
from matplotlib.font_manager import FontProperties
from pathlib import Path

from .utils import *

current_path = os.path.dirname(__file__)


class Text(object):
    """
    地圖上的物件。
    """
    # config
    noto_tc_path = "/Users/ericlwc/Library/Mobile Documents/com~apple~CloudDocs/程式/geo_tools/geotiff_plotting_tools/lib/quickmap/font/NotoSansTC-VariableFont_wght.ttf"

    def __init__(self,
                 text_content: str,
                 font_size: int = 12,
                 font_weight: int = 500,
                 font_color: str = '#1E1E1E',
                 font: str = 'Noto-TC'):
        """
        建立一個文字物件。

        Args
            - text_content: str
                文字內容。
            - font_size: int
                字體大小，預設為 12。
            - font_weight: int 
                字體粗細，預設為 500。
            - font_color: str
                字體顏色，預設為'#1E1E1E'。
            - font: str
                字體，預設為Noto-TC。
            - font_full_properties: FontProperties
                字體的完整屬性。
        """
        self.__text_content = None
        self.__font_size = None
        self.__font_weight = None
        self.__font_color = None
        self.__font = None

        self.text_content = text_content
        self.font_size = font_size
        self.font_weight = font_weight
        self.font_color = font_color
        self.font = font

    @property
    def text_content(self):
        return self.__text_content

    @text_content.setter
    def text_content(self, text_content: str):
        if not isinstance(text_content, str):
            raise TypeError("text_content必須是str。")
        self.__text_content = text_content

    @property
    def font_size(self):
        return self.__font_size

    @font_size.setter
    def font_size(self, font_size: int):
        check_positive(font_size)
        self.__font_size = font_size

    @property
    def font_weight(self):
        return self.__font_weight

    @font_weight.setter
    def font_weight(self, font_weight: int):
        check_positive(font_weight)
        self.__font_weight = font_weight

    @property
    def font_color(self):
        return self.__font_color

    @font_color.setter
    def font_color(self, font_color: str):
        font_color = check_and_convert_color(font_color)
        self.__font_color = font_color

    @property
    def font(self):
        return self.__font

    @font.setter
    def font(self, font: str):
        if not isinstance(font, str):
            raise TypeError("font必須是str。")
        self.__font = font

    def __str__(self):
        return f"Text({self.text_content})"

    def __repr__(self):
        return self.__str__()
