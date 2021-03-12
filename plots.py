from typing import Iterable, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np


def plot_raw(diagram, image_name: str, focus_area: Optional[Tuple] = None, grid_size: float = None) -> None:
    """
    Scatter plot of raw data points.

    :param diagram: The diagram as a pandas dataframe. With columns x, y, z.
    :param image_name: The image name, used in title.
    :param focus_area: Optional coordinates to restrict the plotting area. A Tuple as (x_min, x_max, y_min, y_max).
    :param grid_size: The size of the grid to plot, useful to compare illustrate the pixel interpolation.
    """
    plt.figure(num=None, dpi=250)  # Increase image resolution to see the dots

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
               annotations: Iterable[Tuple[str, List, List]] = None,
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
        for i, (label, region_x, region_y) in enumerate(annotations):
            plt.fill(region_x, region_y, 'b', alpha=min(0.2 + (0.1 * i), 0.9), snap=True)

    plt.imshow(pixels, interpolation='none', cmap='copper',
               extent=[np.min(x_i), np.max(x_i), np.min(y_i), np.max(y_i)])
    plt.title(f'{image_name}\ninterpolated ({interpolation_method}) - pixel size {round(pixel_size, 10) * 1_000}mV')
    plt.xlabel('Gate 1 (V)')
    plt.xticks(rotation=30)
    plt.ylabel('Gate 2 (V)')
    plt.tight_layout()

    if focus_area:
        plt.axis(focus_area)

    plt.show()
