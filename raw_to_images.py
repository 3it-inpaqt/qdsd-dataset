from typing import Iterable, List, Tuple
from zipfile import ZipFile

import matplotlib.pyplot as plt
import numpy as np
import pandas
from scipy.interpolate import griddata


def image_interpolation(diagram, step=0.001, method='nearest', filter_extreme=False):
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


def plot_image(x_i, y_i, pixels, image_name: str, annotations: Iterable[Tuple[List, List]] = None) -> None:
    """
    Plot the interpolated image.
    """

    if annotations is not None:
        # plt.fill([-0.4, -0.3, -0.4], [-0.4, -0.3, -0.3], 'b', alpha=0.5)
        for i, (region_x, region_y) in enumerate(annotations):
            plt.fill(region_x, region_y, 'b', alpha=min(0.2 + (0.1 * i), 0.9), snap=True)

    plt.imshow(pixels, interpolation='none', cmap='copper',
               extent=[np.min(x_i), np.max(x_i), np.min(y_i), np.max(y_i)])
    plt.title(f'{image_name} - interpolated')
    plt.show()


if __name__ == '__main__':
    # Open the zip file and iterate over all csv files
    with ZipFile('data/raw_clean.zip', 'r') as zip_file:
        for diagram_files in zip_file.namelist():
            with zip_file.open(diagram_files) as diagram_file:
                diagram = pandas.read_csv(diagram_file)
                x_i, y_i, pixels = image_interpolation(diagram, filter_extreme=True)
                plot_image(x_i, y_i, pixels, diagram_files)
