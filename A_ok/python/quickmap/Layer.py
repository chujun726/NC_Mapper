"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-06
Description: This module defines a Layer class for quickmap.
"""
from .utils import *

class Layer(object):
    """
    地圖的圖層。

    Attributes
        - is_visible: 圖層是否顯示。

    Methods
        - toggle_visible(): 切換圖層的顯示狀態。
    """

    def __init__(self, is_visible=True):
        self.is_visible = is_visible

    def toggle_visible(self):
        """
        切換圖層的顯示狀態。
        """
        self.is_visible = not self.is_visible