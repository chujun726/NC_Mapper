"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-07
Description: This module defines a title class for quickmap.
"""
from .Text import Text
from .utils import *


class Title(Text):
    """
    地圖的主標題。

    Attributes
        - position: 標題的位置，可以是"left", "center"或"right"。
        - text_content: 標題的內容。
        - font_size: 標題的字體大小。
        - font_weight: 標題的字體粗細。
        - font_color: 標題的字體顏色。
        - font: 標題的字體。
    """
    available_positions = ["left", "center", "right"]

    def __init__(self,
                 text_content: str,
                 position="left",
                 font_size: int = 20,
                 font_weight: int = 600,
                 font_color: str = '#2E2E2E',
                 font: str = "Noto-TC"):
        """
        建立一個主標題。

        Args
            - text_content: str
                標題的內容。
            - position: str
                標題的位置，可以是"left", "center"或"right"，預設為"left"。
            - font_size: int
                標題的字體大小，預設為 20。
            - font_weight: int
                標題的字體粗細，預設為 600。
            - font_color: str
                標題的字體顏色，預設為'#2E2E2E'。
            - font: str
                標題的字體，預設為Noto-TC。
        """
        self.__position = None

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
