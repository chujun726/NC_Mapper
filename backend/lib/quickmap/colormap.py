from matplotlib import cm
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


def calculate_binary_color_map(min_value, max_value) -> dict:
    """
    計算二元分類色階。

    Args
        - min_value: float
            最小值。
        - max_value: float
            最大值。

    Returns
        - value_color_dict: dict
            值和顏色的對應字典，格式為{值: 顏色}。
    """
    # set the color map
    value_color_dict = {min_value: "blue", 0: "white", max_value: "red"}
    return value_color_dict


def calculate_continuous_color_map(min_value, max_value, cmap_name="jet") -> dict:
    """
    計算連續色階。

    Args
        - min_value: float
            最小值。
        - max_value: float
            最大值。
        - cmap_name: str
            色階名稱。

    Returns
        - value_color_dict: dict
            值和顏色的對應字典，格式為{值: 顏色}。
    """
    # get the color map
    norm = mpl.colors.Normalize(vmin=min_value, vmax=max_value)
    cmap = plt.get_cmap(cmap_name)
    mappable = cm.ScalarMappable(norm=norm, cmap=cmap)

    # calculate the color map
    value_color_dict = {}
    for value in np.linspace(min_value, max_value, 100):
        color = mappable.to_rgba(value)
        value_color_dict[value] = color

    return value_color_dict


def calculate_binary_color_map_ticks(min_value, max_value) -> list:
    """
    計算二元分類色階的刻度。

    Args
        - min_value: float
            最小值。
        - max_value: float
            最大值。

    Returns
        - ticks: list
            刻度的值。
    """
    ticks = [min_value, 0, max_value]
    return ticks


def calculate_continuous_color_map_ticks(min_value, max_value) -> list:
    """
    計算連續色階的刻度。

    Args
        - min_value: float
            最小值。
        - max_value: float
            最大值。

    Returns
        - ticks: list
            刻度的值。
    """
    ticks = np.linspace(min_value, max_value, 5)
    return ticks
