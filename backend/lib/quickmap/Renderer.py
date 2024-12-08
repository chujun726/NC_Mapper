"""
Author: ericlwc (github: ericlwc0830)
Date: 2024-11-09
Description: This module renders a map based on the map description.
"""
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
import rasterio

from .CoastlineLayer import CoastlineLayer
from .ContourLayer import ContourLayer
from .CountriesBorderLayer import CountriesBorderLayer
from .FeatureLayer import FeatureLayer
from .GridLineLayer import GridLineLayer
from .LakesLayer import LakesLayer
from .MapDescription import MapDescription
from .RiversLayer import RiversLayer
from .ShadingLayer import ShadingLayer
from .Text import Text


current_path = os.path.dirname(os.path.abspath(__file__))


class Renderer(object):
    """
    渲染器物件，用於根據地圖描述物件渲染地圖。

    Attributes:
        map_description: MapDescription
            地圖描述物件。
        map_fig: matplotlib.figure.Figure
            地圖的圖片物件。
        ax: matplotlib.axes.Axes
            地圖的軸物件。
        im: matplotlib.image.AxesImage
            地圖的影像物件。

    Methods:
        render(save_at=None)
            根據地圖描述物件渲染地圖。
    """

    def __init__(self, map_description: MapDescription):
        self.map_description = map_description
        self.map_fig = None
        self.ax = None
        self.im = None

    def render(self, save_at=None):
        # load attributes
        map_description = self.map_description
        layer_list = map_description.layer_list

        # render map
        self._create_figure()
        z_order = 0
        for layer in layer_list.get_list():
            self._plot_layer(layer, z_order)
            z_order += 1
        self._add_colorbar()
        self._add_subtitle()
        self._add_title()
        self._add_remark()

        # save figure
        if save_at:
            plt.savefig(save_at, bbox_inches='tight', pad_inches=0.5)

    def _create_figure(self):
        # load map description
        map_description = self.map_description
        canvas = map_description.canvas

        # load canvas information
        projection = canvas.display_projection_crs
        x_left = canvas.x_left
        x_right = canvas.x_right
        if x_right < x_left:
            x_right += 360
        y_min = canvas.y_min
        y_max = canvas.y_max
        edge_color = canvas.edge_color
        edge_width = canvas.edge_width
        extent = [x_left, x_right, y_min, y_max]

        # create a figure
        map_fig = plt.figure(figsize=(15, 15), dpi=100, facecolor=(1, 1, 1, 0))
        ax = plt.axes(projection=projection)

        # set figure extent
        if isinstance(projection, ccrs.Orthographic):
            # Orthographic projection does not support extent (avoid plotting error)
            ax.set_global()
        else:
            ax.set_extent(extent, crs=ccrs.PlateCarree())

        # set edge color and width
        for edge in ax.spines.values():
            edge.set_zorder(1000000)
            edge.set_edgecolor(edge_color)
            edge.set_linewidth(edge_width)

        # save to class attribute
        self.ax = ax
        self.map_fig = map_fig

    def _plot_layer(self, layer, z_order):
        if isinstance(layer, CoastlineLayer):
            self._plot_coastlinelayer(layer, z_order)
        elif isinstance(layer, CountriesBorderLayer):
            self._plot_countriesborderlayer(layer, z_order)
        elif isinstance(layer, RiversLayer):
            self._plot_riverslayer(layer, z_order)
        elif isinstance(layer, LakesLayer):
            self._plot_lakeslayer(layer, z_order)
        elif isinstance(layer, ShadingLayer):
            im = self._plot_shadinglayer(layer, z_order)
            self.im = im
        elif isinstance(layer, GridLineLayer):
            self._plot_gridlinelayer(layer, z_order)
        elif isinstance(layer, FeatureLayer):
            self._plot_featurelayer(layer, z_order)
        elif isinstance(layer, ContourLayer):
            self._plot_contourlayer(layer, z_order)

    def _plot_coastlinelayer(self, layer, z_order):
        if not layer.is_visible:
            return

        feature_path = f"{current_path}/map_feature/coastline/coastline_{layer.resolution}/coastline_{layer.resolution}.shp"
        coastline_layer = cfeature.ShapelyFeature(
            Reader(feature_path).geometries(),
            ccrs.PlateCarree(),
            facecolor=layer.face_color,
            edgecolor=layer.line_color,
            linewidth=layer.line_width)

        self.ax.add_feature(coastline_layer, zorder=z_order)

    def _plot_countriesborderlayer(self, layer, z_order):
        if not layer.is_visible:
            return

        feature_path = f"{current_path}/map_feature/countries/countries_{layer.resolution}/countries_{layer.resolution}.shp"
        countries_layer = cfeature.ShapelyFeature(
            Reader(feature_path).geometries(),
            ccrs.PlateCarree(),
            facecolor=layer.face_color,
            edgecolor=layer.line_color,
            linewidth=layer.line_width)

        self.ax.add_feature(countries_layer, zorder=z_order)

    def _plot_riverslayer(self, layer, z_order):
        if not layer.is_visible:
            return

        feature_path = f"{current_path}/map_feature/rivers/rivers_{layer.resolution}/rivers_{layer.resolution}.shp"
        rivers_layer = cfeature.ShapelyFeature(
            Reader(feature_path).geometries(),
            ccrs.PlateCarree(),
            facecolor=layer.face_color,
            edgecolor=layer.line_color,
            linewidth=layer.line_width)

        self.ax.add_feature(rivers_layer, zorder=z_order)

    def _plot_lakeslayer(self, layer, z_order):
        if not layer.is_visible:
            return

        feature_path = f"{current_path}/map_feature/lakes/lakes_{layer.resolution}/lakes_{layer.resolution}.shp"
        lakes_layer = cfeature.ShapelyFeature(
            Reader(feature_path).geometries(),
            ccrs.PlateCarree(),
            facecolor=layer.face_color,
            edgecolor=layer.line_color,
            linewidth=layer.line_width)

        self.ax.add_feature(lakes_layer, zorder=z_order)

    def _plot_shadinglayer(self, layer, z_order):
        if not layer.is_visible:
            return

        # read data
        data = layer.data
        value_type = layer.value_type
        interpolation = layer.interpolation
        west_bound = layer.west_bound
        east_bound = layer.east_bound
        south_bound = layer.south_bound
        north_bound = layer.north_bound
        extent = [west_bound, east_bound, south_bound, north_bound]
        crs = layer.crs
        if crs == rasterio.crs.CRS.from_epsg(4326):
            crs = ccrs.PlateCarree()

        # set colorbar
        value_color_dict = layer.value_color_dict
        colors = list(value_color_dict.values())
        nodes = list(value_color_dict.keys())
        nodes_min = min(nodes)
        nodes_max = max(nodes)
        nodes_normalized = [(node - nodes_min) / (nodes_max - nodes_min) for node in nodes]
        if value_type == "continuous":
            cmap = mcolors.LinearSegmentedColormap.from_list("custom_cmap", list(zip(nodes_normalized, colors)))
            norm = mcolors.Normalize(vmin=nodes_min, vmax=nodes_max)
        elif value_type == "discrete":
            cmap = mcolors.ListedColormap(list(colors), name="custom_cmap", N=len(nodes))
            boundaries = nodes + [nodes_max + (nodes_max - nodes_min)*0.1]
            norm = mcolors.BoundaryNorm(boundaries=boundaries, ncolors=len(colors), clip=False)

        # plot
        im = self.ax.imshow(data,
                            origin='upper',
                            extent=extent,
                            transform=crs,
                            cmap=cmap,
                            norm=norm,
                            interpolation=interpolation)

        # set zorder
        im.set_zorder(z_order)

        return im

    def _plot_featurelayer(self, layer, z_order):
        if not layer.is_visible:
            return

        # load attributes
        gdf = layer.data
        edge_default_color = layer.edge_default_color
        edge_dynamic_color = layer.edge_dynamic_color
        edge_width = layer.edge_width
        face_default_color = layer.face_default_color
        face_dynamic_color = layer.face_dynamic_color
        layer_marker = layer.marker
        value_type = layer.value_type
        feature_type = layer.feature_type

        # set colorbar
        if layer.has_value:
            value_color_dict = layer.value_color_dict
            colors = list(value_color_dict.values())
            nodes = list(value_color_dict.keys())
            nodes_min = min(nodes)
            nodes_max = max(nodes)
            nodes_normalized = [(node - nodes_min) / (nodes_max - nodes_min) for node in nodes]

        if layer.has_value and value_type == "continuous":
            cmap = mcolors.LinearSegmentedColormap.from_list("custom_cmap", list(zip(nodes_normalized, colors)))
            norm = mcolors.Normalize(vmin=nodes_min, vmax=nodes_max)
        elif layer.has_value and value_type == "discrete":
            cmap = mcolors.ListedColormap(list(colors), name="custom_cmap", N=len(nodes))
            boundaries = nodes + [nodes_max + (nodes_max - nodes_min)*0.1]
            norm = mcolors.BoundaryNorm(boundaries=boundaries, ncolors=len(colors), clip=False)

        # plot
        if feature_type == "Point":
            for idx, row in gdf.iterrows():
                x = row.geometry.x
                y = row.geometry.y
                marker = layer_marker
                marker_size = edge_width
                if layer.has_value:
                    value = row["value"]

                if not layer.has_value:
                    color = edge_default_color
                elif layer.has_value and not edge_dynamic_color:
                    color = edge_default_color
                elif layer.has_value and edge_dynamic_color:
                    color = cmap(norm(value))

                self.ax.plot(x, y,
                             marker=marker,
                             markersize=marker_size,
                             color=color,
                             zorder=z_order,
                             transform=ccrs.PlateCarree())
        elif feature_type == "Polygon" or feature_type == "MultiPolygon":
            for idx, row in gdf.iterrows():
                geometry = row.geometry
                marker = layer_marker
                if layer.has_value:
                    value = row[layer["value"]]

                if not layer.has_value:
                    edge_color = edge_default_color
                elif layer.has_value and not edge_dynamic_color:
                    edge_color = edge_default_color
                elif layer.has_value and edge_dynamic_color:
                    edge_color = cmap(norm(value))

                if not layer.has_value:
                    face_color = face_default_color
                elif layer.has_value and face_dynamic_color:
                    face_color = face_default_color
                elif layer.has_value and not face_dynamic_color:
                    face_color = cmap(norm(value))

                self.ax.add_geometries(geometry,
                                       crs=ccrs.PlateCarree(),
                                       facecolor=face_color,
                                       edgecolor=edge_color,
                                       linewidth=edge_width,
                                       zorder=z_order)

    def _plot_gridlinelayer(self, layer, z_order):
        if not layer.is_visible:
            return

        # load attributes
        plot_at_lat = layer.plot_at_lat
        plot_at_lon = layer.plot_at_lon
        line_color = layer.line_color
        line_width = layer.line_width
        label_size = layer.label_size
        label_color = layer.label_color
        label_weight = layer.label_weight
        label_font = layer.label_font
        font_properties = self._get_font_properties(label_font, label_size, label_weight)

        # plot gridlines
        gridlines = self.ax.gridlines(
            draw_labels=True,
            x_inline=False,
            y_inline=False,
            linewidth=line_width,
            color=line_color,
            zorder=z_order)

        # set gridlines location and format
        gridlines.xlocator = mpl.ticker.FixedLocator(plot_at_lon)
        gridlines.ylocator = mpl.ticker.FixedLocator(plot_at_lat)

        # set gridlines label
        gridlines.top_labels = False
        if self.map_description.layer_of_colorbar is None:
            gridlines.right_labels = True
        else:
            gridlines.right_labels = False
        gridlines.xlabel_style = {'rotation': 20}
        gridlines.xlabel_style.update({'fontproperties': font_properties, 'color': label_color})
        gridlines.ylabel_style.update({'fontproperties': font_properties, 'color': label_color})
        gridlines.xformatter = mpl.ticker.FuncFormatter(lambda x, pos: f"{round(x,3)}°" if x % 1 else f"{int(x)}°")
        gridlines.yformatter = mpl.ticker.FuncFormatter(lambda y, pos: f"{round(y,3)}°" if y % 1 else f"{int(y)}°")
        gridlines.xlines = True
        gridlines.ylines = True

    def _plot_contourlayer(self, layer, z_order):
        if not layer.is_visible:
            return

        # load attributes
        data = layer.data
        value_base = layer.value_base
        value_interval = layer.value_interval
        primary_contour_each = layer.primary_contour_each
        line_color = layer.line_color
        line_width = layer.line_width
        min_of_original_data = layer.min_of_original_data
        max_of_original_data = layer.max_of_original_data
        font_size = layer.font_size
        font_color = layer.font_color
        label_format = layer.label_format
        ax = self.ax

        # get data xy grid
        lon_list = layer.lon_list
        lat_list = layer.lat_list
        X, Y = np.meshgrid(lon_list, lat_list)

        # calculate primary contour levels
        if primary_contour_each is None:
            primary_contour_levels = []
        else:
            primary_contour_levels_1 = np.arange(value_base, max_of_original_data, value_interval*primary_contour_each)  # 大於基值的首曲線
            primary_contour_levels_2 = np.arange(value_base, min_of_original_data, -value_interval*primary_contour_each)  # 小於基值的首曲線
            primary_contour_levels_2 = primary_contour_levels_2[1:]
            primary_contour_levels = np.concatenate((primary_contour_levels_2, primary_contour_levels_1))
            primary_contour_levels = primary_contour_levels.tolist()
            primary_contour_levels = list(set(primary_contour_levels))
            primary_contour_levels = sorted(primary_contour_levels)

        # calculate intermediate contour levels
        contour_levels_1 = np.arange(value_base, max_of_original_data, value_interval)
        contour_levels_2 = np.arange(value_base, min_of_original_data, -value_interval)
        contour_levels = np.concatenate((contour_levels_2, contour_levels_1))
        contour_levels = contour_levels.tolist()
        contour_levels = list(set(contour_levels))
        intermediate_contour_levels = [level for level in contour_levels if level not in primary_contour_levels]
        intermediate_contour_levels = sorted(intermediate_contour_levels)

        # set color
        line_color = mpl.colors.to_hex(line_color)
        font_color = mpl.colors.to_hex(font_color)

        # 繪製計曲線
        intermediate_contour = ax.contour(
            X, Y, data,
            levels=intermediate_contour_levels,
            colors=line_color,
            linewidths=line_width,
            transform=ccrs.PlateCarree(),  # 如果數據在經緯度坐標系統下
            zorder=z_order)

        # 繪製首曲線
        primary_contour = ax.contour(
            X, Y, data,
            levels=primary_contour_levels,
            colors=line_color,
            linewidths=line_width * 2,
            transform=ccrs.PlateCarree(),
            zorder=z_order)

        # 添加等高線標籤
        clabel = ax.clabel(
            primary_contour,
            levels=primary_contour_levels,
            fmt=label_format,
            fontsize=font_size,
            colors=font_color)

        # set zorder for clabel
        for text in clabel:
            text.set_zorder(z_order)

    def _add_colorbar(self):
        layer_of_colorbar = self.map_description.layer_of_colorbar
        if layer_of_colorbar is None:
            plot_colorbar_for_featurelayer = False
            plot_colorbar_for_shadinglayer = False
            return

        if isinstance(layer_of_colorbar, ShadingLayer):
            plot_colorbar_for_shadinglayer = True
            plot_colorbar_for_featurelayer = False

        elif isinstance(layer_of_colorbar, FeatureLayer) and not layer_of_colorbar.has_value:
            plot_colorbar_for_featurelayer = False
            plot_colorbar_for_shadinglayer = False

        elif isinstance(layer_of_colorbar, FeatureLayer) and layer_of_colorbar.has_value:
            plot_colorbar_for_shadinglayer = False
            plot_colorbar_for_featurelayer = True

        else:
            raise TypeError("colorbar layer must be either ShadingLayer or FeatureLayer.")

        if plot_colorbar_for_shadinglayer:
            # load attributes
            map_description = self.map_description
            map_fig = self.map_fig
            ax = self.ax
            im = self.im

            # load map description
            shading_layer = layer_of_colorbar
            colorbar = map_description.colorbar
            height_fraction = colorbar.height_fraction
            ticks_font_size = colorbar.ticks_font_size
            ticks_font_weight = colorbar.ticks_font_weight
            ticks_font_color = colorbar.ticks_font_color
            ticks_font = colorbar.ticks_font
            ticks_font_properties = self._get_font_properties(ticks_font, ticks_font_size, ticks_font_weight)
            label_title_font_size = colorbar.label_title_font_size
            label_title_font_weight = colorbar.label_title_font_weight
            label_title_font_color = colorbar.label_title_font_color
            label_title_font = colorbar.label_title_font
            label_title_font_properties = self._get_font_properties(label_title_font, label_title_font_size, label_title_font_weight)

            # set colorbar
            if shading_layer is not None:
                cbar = plt.colorbar(
                    im,
                    ax=ax,
                    orientation="vertical",
                    pad=0.01,
                    extend=shading_layer.colorbar_extend,
                    location="right",
                    ticks=shading_layer.colorbar_ticks,
                )
                map_bbox = map_fig.axes[0].get_position()
                cbar.ax.set_position([map_bbox.x1 + 0.01, map_bbox.y0, 0.01, map_bbox.height*height_fraction])

                # set colorbar ticks's label font properties
                for tick_label in cbar.ax.get_yticklabels():
                    tick_label.set_fontproperties(ticks_font_properties)
                    tick_label.set_color(ticks_font_color)

                # set colorbar label with font properties
                cbar.ax.set_title(
                    shading_layer.colorbar_title_label,
                    fontproperties=label_title_font_properties,
                    color=label_title_font_color,
                    loc='left',
                    pad=20,
                )

        elif plot_colorbar_for_featurelayer:
            # load attributes
            map_description = self.map_description
            map_fig = self.map_fig
            ax = self.ax

            # load map description
            feature_layer = layer_of_colorbar
            colorbar = map_description.colorbar
            height_fraction = colorbar.height_fraction
            ticks_font_size = colorbar.ticks_font_size
            ticks_font_weight = colorbar.ticks_font_weight
            ticks_font_color = colorbar.ticks_font_color
            ticks_font = colorbar.ticks_font
            ticks_font_properties = self._get_font_properties(ticks_font, ticks_font_size, ticks_font_weight)
            label_title_font_size = colorbar.label_title_font_size
            label_title_font_weight = colorbar.label_title_font_weight
            label_title_font_color = colorbar.label_title_font_color
            label_title_font = colorbar.label_title_font
            label_title_font_properties = self._get_font_properties(label_title_font, label_title_font_size, label_title_font_weight)

            # set colorbar
            if feature_layer is not None:
                # Prepare cmap and norm
                value_color_dict = feature_layer.value_color_dict
                colors = list(value_color_dict.values())
                nodes = list(value_color_dict.keys())
                nodes_min = min(nodes)
                nodes_max = max(nodes)
                nodes_normalized = [(node - nodes_min) / (nodes_max - nodes_min) for node in nodes]
                if feature_layer.value_type == "continuous":
                    cmap = mcolors.LinearSegmentedColormap.from_list("custom_cmap", list(zip(nodes_normalized, colors)))
                    norm = mcolors.Normalize(vmin=nodes_min, vmax=nodes_max)
                elif feature_layer.value_type == "discrete":
                    cmap = mcolors.ListedColormap(list(colors), name="custom_cmap", N=len(nodes))
                    boundaries = nodes + [nodes_max + (nodes_max - nodes_min)*0.1]
                    norm = mcolors.BoundaryNorm(boundaries=boundaries, ncolors=len(colors), clip=False)

                # Create a ScalarMappable
                sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])  # Only needed for matplotlib < 3.1

                cbar = plt.colorbar(
                    sm,
                    ax=ax,
                    orientation="vertical",
                    pad=0.01,
                    extend=feature_layer.colorbar_extend,
                    ticks=feature_layer.colorbar_ticks,
                    location="right",
                )
                map_bbox = map_fig.axes[0].get_position()
                cbar.ax.set_position([map_bbox.x1 + 0.01, map_bbox.y0, 0.01, map_bbox.height * height_fraction])

                # set colorbar ticks's label font properties
                for tick_label in cbar.ax.get_yticklabels():
                    tick_label.set_fontproperties(ticks_font_properties)
                    tick_label.set_color(ticks_font_color)

                # set colorbar label with font properties
                cbar.ax.set_title(
                    feature_layer.colorbar_title_label,
                    fontproperties=label_title_font_properties,
                    color=label_title_font_color,
                    loc='left',
                    pad=20,
                )

    def _add_subtitle(self):
        # load attributes
        map_description = self.map_description
        subtitle = map_description.subtitle
        ax = self.ax
        map_fig = self.map_fig

        # plot subtitle
        canvas_height = ax.get_position().y1 - ax.get_position().y0
        delta_position_y = (subtitle.font_size * (1/3)) / (canvas_height * map_fig.dpi * map_fig.get_figheight())
        position_y = 1 + delta_position_y
        if subtitle.text_content is None or subtitle.text_content == "":
            return
        else:
            subtitle_text_box = self._add_textbox(subtitle, position_y)

        self.subtitle_text_box = subtitle_text_box
        return subtitle_text_box

    def _add_title(self):
        # load attributes
        map_description = self.map_description
        title = map_description.title
        ax = self.ax

        # load map description
        try:
            subtitle_text_box = self.subtitle_text_box
            have_subtitle = True
        except AttributeError:
            have_subtitle = False

        # set title position_y
        canvas_height = ax.get_position().y1 - ax.get_position().y0
        delta_position_y = (title.font_size * (1/3)) / (canvas_height * self.map_fig.dpi * self.map_fig.get_figheight())
        if have_subtitle:
            ax_renderer = ax.figure.canvas.get_renderer()
            bbox = subtitle_text_box.get_window_extent(renderer=ax_renderer)
            inv_transform = ax.transAxes.inverted()
            bbox_transformed = inv_transform.transform(bbox)
            position_y = bbox_transformed[1, 1] + delta_position_y
        else:
            position_y = 1 + delta_position_y

        # plot title
        if title.text_content is None or title.text_content == "":
            return
        else:
            title_text_box = self._add_textbox(title, position_y)
            title_text_box.set_va("bottom")

        self.title_text_box = title_text_box
        return title_text_box

    def _add_remark(self):
        # load attributes
        map_description = self.map_description
        ax = self.ax

        # load map description
        remark = map_description.remark

        # plot remark
        if remark.text_content is None or remark.text_content == "":
            return
        else:
            position_y = -0.01
            remark_text_box = self._add_textbox(remark, position_y)

        # modify remark position
        renderer = ax.figure.canvas.get_renderer()
        x_tick_labels = ax.get_xticklabels()
        if x_tick_labels:
            bbox = x_tick_labels[0].get_window_extent(renderer=renderer)
            inv_transform = ax.transAxes.inverted()
            bbox_transformed = inv_transform.transform(bbox)
            padding = 0.03
            remark_text_box.set_position((0, bbox_transformed[0, 1] - padding))
            remark_text_box.set_va("top")

        self.__remark_text_box = remark_text_box
        return remark_text_box

    @staticmethod
    def _get_font_properties(font_name, font_size, font_weight):
        """
        創建字體屬性，如果字體名稱是mpl的字體，則使用mpl的字體，若是自定義字體，則自動查找字體ttf檔案路徑。

        Args:
            font_name: str
                字體名稱。
            font_size: int
                字體大小。
            font_weight: int
                字體粗細。
        """
        font_path = f"{current_path}/font/{font_name}/{font_weight}.ttf"
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"字體檔案不存在：{font_path}")

        font_properties = mpl.font_manager.FontProperties(
            fname=font_path,
            size=font_size,
            weight=font_weight)

        return font_properties

    def _add_textbox(self, description, position_y):
        if not isinstance(description, Text):
            raise TypeError("description必須是Text的子類別。")

        if description is None:
            return

        # load description information
        font = description.font
        font_size = description.font_size
        font_weight = description.font_weight
        text_content = description.text_content
        position = description.position
        font_color = description.font_color
        font_properties = self._get_font_properties(font, font_size, font_weight)

        # set subtitle position
        if position == "right":
            position_x = 1
            position_y = position_y
            ha = "right"
        elif position == "center":
            position_x = 0.5
            position_y = position_y
            ha = "center"
        elif position == "left":
            position_x = 0
            position_y = position_y
            ha = "left"
        else:
            raise ValueError("position must be 'left', 'center' or 'right'.")

        # add subtitle
        subtitle_text_box = self.ax.text(
            position_x,
            position_y,
            text_content,
            color=font_color,
            ha=ha,
            va='bottom',
            transform=self.ax.transAxes,
            fontproperties=font_properties,
        )

        return subtitle_text_box
