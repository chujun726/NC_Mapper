"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-06
Description: This module defines a LayerList class for quickmap.
"""
from .Layer import Layer
from .ShadingLayer import ShadingLayer
from .utils import *


class LayerList(list):
    """
    地圖的圖層列表。

    Attributes
        - count: 圖層數量。

    Methods
        - get_list(): 取得圖層列表。
        - show: 顯示所有圖層。
        - add(layer): 新增圖層於最上層。
        - remove(layer): 移除圖層。
        - move_up(layer): 圖層上移。
        - move_down(layer): 圖層下移。
        - move_top(layer): 圖層移到最上層。
        - move_bottom(layer): 圖層移到最下層。
        - clear(): 清除所有圖層。
        - select_layer_by_class(class_name): 找出所有屬於特定類別的圖層。
    """

    def __init__(self):
        self.__layers = []

    @property
    def count(self):
        """
        圖層數量。
        """
        return len(self.__layers)

    def get_list(self):
        """
        取得圖層列表。
        """
        return self.__layers

    def show(self):
        """
        顯示所有圖層。
        """
        for layer in self.__layers:
            print(layer)

    def add(self, layer):
        """
        新增圖層於最上層。
        """
        # check if layer is inherited from Layer
        if not isinstance(layer, Layer):
            raise TypeError("layer must be an instance of Layer")

        # check if layer is already in the list
        if layer in self.__layers:
            raise ValueError("layer is already in the list")

        # multiple shading layers are not allowed
        if isinstance(layer, ShadingLayer):
            for l in self.__layers:
                if isinstance(l, ShadingLayer):
                    raise ValueError("multiple shading layers are not allowed")

        self.__layers.append(layer)

    def remove(self, layer):
        """
        移除圖層。
        """
        self.__layers.remove(layer)

    def move_up(self, layer):
        """
        圖層上移。
        """
        index = self.__layers.index(layer)
        if index != len(self.__layers) - 1:
            self.__layers.insert(index + 1, self.__layers.pop(index))

    def move_down(self, layer):
        """
        圖層下移。
        """
        index = self.__layers.index(layer)
        if index != 0:
            self.__layers.insert(index - 1, self.__layers.pop(index))

    def move_top(self, layer):
        """
        圖層移到最上層。
        """
        self.__layers.remove(layer)
        self.__layers.append(layer)

    def move_bottom(self, layer):
        """
        圖層移到最下層。
        """
        self.__layers.remove(layer)
        self.__layers.insert(0, layer)

    def clear(self):
        """
        清除所有圖層。
        """
        self.__layers.clear()

    def select_layers_by_class(self, class_name):
        """
        找出所有屬於特定類別的圖層。

        Args
            - class_name: class
                類別名稱。

        Returns
            - layers: list
                所有屬於特定類別的圖層。
        """
        layers = []
        for layer in self.__layers:
            if isinstance(layer, class_name):
                layers.append(layer)
        return layers

    def __str__(self):
        return str(self.__layers)

    def __repr__(self):
        print("if you want to see the list of layers, please use layer_list.get_list() method.")
        return str(self.__layers)
