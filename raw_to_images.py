from typing import Iterable, List, Optional, Tuple
from zipfile import ZipFile

import matplotlib.pyplot as plt
import numpy as np
import pandas
from matplotlib.pyplot import figure
from scipy.interpolate import griddata


def image_interpolation(diagram, step=0.001, method='nearest', filter_extreme=False) -> Tuple:
    """
    Convert a set of irregular point into pixels using interpolation.

    :param diagram: The diagram as a pandas dataframe. With columns x, y, z.
    :param step: The output grid resolution.
    :param method: The interpolation method.
    (see https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html)
    :param filter_extreme: If true limit the z values between the first and the last percentile.
    :return The x axes, the y axes, the 2D array representing the image.
    """
    if filter_extreme:
        # Limit z values between the 1st and 99th percentile to avoid visual issues with extreme values
        percentile1 = np.percentile(diagram.z, 1)
        percentile99 = np.percentile(diagram.z, 99)
        diagram.loc[diagram.z < percentile1, 'z'] = percentile1
        diagram.loc[diagram.z > percentile99, 'z'] = percentile99

    # Remove one pixel around to avoid rounding issues during the interpolation
    x_i = np.arange(np.min(diagram.x) + step, np.max(diagram.x), step)
    y_i = np.arange(np.min(diagram.y) + step, np.max(diagram.y), step)
    x_i, y_i = np.meshgrid(x_i, y_i)

    # Use nearest interpolation method.
    grid = griddata((diagram.x, diagram.y), diagram.z, (x_i, y_i), method=method)

    # Flip the grid to keep the same direction (I don't know why it's inverted during the interpolation)
    grid = np.flip(grid, axis=0)
    return x_i, y_i, grid


def plot_raw(diagram, image_name: str, focus_area: Optional[Tuple] = None, grid_size: float = None) -> None:
    """
    Scatter plot of raw data points.

    :param diagram: The diagram as a pandas dataframe. With columns x, y, z.
    :param image_name: The image name, used in title.
    :param focus_area: Optional coordinates to restrict the plotting area. A Tuple as (x_min, x_max, y_min, y_max).
    :param grid_size: The size of the grid to plot, useful to compare illustrate the pixel interpolation.
    """
    figure(num=None, dpi=250)  # Increase image resolution to see the dots

    # Draw the grid
    # FIXME the grid lines doesn't match with pixels because they don't start at 0
    if grid_size:
        for i in np.arange(min(diagram.y), max(diagram.y), grid_size):
            plt.axhline(i, linestyle='-', color='lightgrey', linewidth=1, zorder=0)
        for i in np.arange(min(diagram.x), max(diagram.x), grid_size):
            plt.axvline(i, linestyle='-', color='lightgrey', linewidth=1, zorder=0)

    plt.scatter(diagram.x, diagram.y, c=diagram.z, cmap='copper', s=1, zorder=10)

    plt.title(f'{image_name} - raw' + (f' (grid {grid_size})' if grid_size else ''))

    # Select only a part of the plot
    if focus_area:
        plt.axis(focus_area)

    plt.show(dpi=200)


def plot_image(x_i, y_i, pixels, image_name: str, interpolation_method: str, pixel_size: float,
               annotations: Iterable[Tuple[List, List]] = None,
               focus_area: Optional[Tuple] = None) -> None:
    """
    Plot the interpolated image.

    :param x_i: The x coordinates of the pixels (post interpolation)
    :param y_i: The y coordinates of the pixels (post interpolation)
    :param pixels: The list of pixels to plot
    :param image_name: The name of the image, used for plot title
    :param interpolation_method: The pixels interpolation method, used for plot title
    :param pixel_size: The size of pixels, in voltage, used for plot title
    :param annotations: The annotation to draw on top of the image
    :param focus_area: Optional coordinates to restrict the plotting area. A Tuple as (x_min, x_max, y_min, y_max).
    """

    if annotations is not None:
        # plt.fill([-0.4, -0.3, -0.4], [-0.4, -0.3, -0.3], 'b', alpha=0.5)
        for i, (region_x, region_y) in enumerate(annotations):
            plt.fill(region_x, region_y, 'b', alpha=min(0.2 + (0.1 * i), 0.9), snap=True)

    plt.imshow(pixels, interpolation='none', cmap='copper',
               extent=[np.min(x_i), np.max(x_i), np.min(y_i), np.max(y_i)])
    plt.title(f'{image_name}\ninterpolated ({interpolation_method}) - pixel size {pixel_size}')

    if focus_area:
        plt.axis(focus_area)

    plt.show()


if __name__ == '__main__':
    pixel_size = 0.0025
    interpolation_method = 'nearest'

    # Open the zip file and iterate over all csv files
    with ZipFile('data/raw_clean.zip', 'r') as zip_file:
        for diagram_files in zip_file.namelist():
            with zip_file.open(diagram_files) as diagram_file:
                # Plot a specific area of the diagram
                # focus_area = None
                focus_area = (-0.460, -0.440, -0.65, -0.63)

                # Load data
                diagram = pandas.read_csv(diagram_file)

                # Plot raw points
                plot_raw(diagram, diagram_files, focus_area, grid_size=None)

                # Interpolate and plot image
                x_i, y_i, pixels = image_interpolation(diagram,
                                                       method=interpolation_method,
                                                       step=pixel_size,
                                                       filter_extreme=True)
                plot_image(x_i, y_i, pixels, diagram_files, interpolation_method, pixel_size, focus_area=focus_area)
                # break
