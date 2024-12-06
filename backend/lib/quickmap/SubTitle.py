"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-07
Description: This module defines a subtitle class for quickmap.
"""
from .Text import Text
from .utils import *


class SubTitle(Text):
    """
    地圖的副標題。

    Attributes
        - position: 副標題的位置，可以是"left", "center"或"right"。
        - text_content: 副標題的內容。
        - font_size: 副標題的字體大小。
        - font_weight: 副標題的字體粗細。
        - font_color: 副標題的字體顏色。
        - font: 副標題的字體。
    """
    available_positions = ["left", "center", "right"]

    def __init__(self,
                 text_content: str,
                 position: str = "left",
                 font_size: int = 16,
                 font_weight: int = 200,
                 font_color: str = '#1E1E1E',
                 font: str = 'Noto-TC'):
        """
        建立一個副標題。

        Args
            - text_content: str
                副標題的內容。
            - position: str
                副標題的位置，可以是"left", "center"或"right"，預設為"left"。
            - font_size: int
                副標題的字體大小，預設為 18。
            - font_weight: int
                副標題的字體粗細，預設為 200。
            - font_color: str
                副標題的字體顏色，預設為'#1E1E1E'。
            - font: str
                副標題的字體，預設為Noto-TC。
        """
        super().__init__(text_content, font_size, font_weight, font_color, font)
        self.position = position

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, position: str):
        if not isinstance(position, str):
            raise TypeError("position必須是str。")
        if position not in self.available_positions:
            raise ValueError("position必須是'left', 'center'或'right'之一。")
        self.__position = position
