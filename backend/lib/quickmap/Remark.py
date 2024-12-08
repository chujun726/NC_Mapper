"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-07
Description: This module defines a remark class for quickmap.
"""
from .Text import Text
from .Title import Title
from .utils import *


class Remark(Text):
    """
    地圖 備註。

    Attributes
        - position: 備註的位置，可以是"left", "center"或"right"。
        - text_content: 備註的內容。
        - font_size: 備註的字體大小。
        - font_weight: 備註的字體粗細。
        - font_color: 備註的字體顏色。
        - font: 備註的字體。
    """

    def __init__(self,
                 text_content: str,
                 position: str = "left",
                 font_size: int = 10,
                 font_weight: int = 400,
                 font_color: str = '#1E1E1E',
                 font: str = 'Noto-TC'):
        """
        建立一個備註。

        Args
            - text_content: str
                備註的內容。
            - position: str
                備註的位置，可以是"left", "center"或"right"，預設為"left"。
            - font_size: int
                備註的字體大小，預設為 8。
            - font_weight: int
                備註的字體粗細，預設為 500。
            - font_color: str
                備註的字體顏色，預設為'#1E1E1E'。
            - font: str
                備註的字體，預設為Noto-TC。
        """
        super().__init__(text_content, font_size, font_weight)
        self.position = position

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, position: str):
        if not isinstance(position, str):
            raise TypeError("position必須是str。")
        if position not in Title.available_positions:
            raise ValueError("position必須是'left', 'center'或'right'之一。")
        self.__position = position
