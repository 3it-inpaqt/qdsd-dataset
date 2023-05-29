import gc
from pathlib import Path
from typing import IO, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas
from scipy.interpolate import griddata

from dataset_label import DatasetLabel
from plots import plot_image, plot_raw
from settings import settings

DATA_DIR = Path(settings.data_dir)
OUT_DIR = Path(settings.out_dir)


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

    # Use "nearest" interpolation method.
    grid = griddata((diagram.x, diagram.y), diagram.z, (x_i, y_i), method=method)

    # Flip the grid to keep the same direction (I don't know why it's inverted during the interpolation)
    grid = np.flip(grid, axis=0)
    return x_i, y_i, grid


def save_images(file_dir: Path, file_basename: str, pixels, interpolation_method: str, pixel_size: float,
                filter_extreme=True) -> None:
    """
    Save interpolated image in 3 versions:
        * Pixels color represent the normalized current value
        * Pixels color represent the derivative in respect to the x-axis
        * Pixels color represent the derivative in respect to the y-axis

    :param file_dir: The path to the directory where to save the image
    :param file_basename: The name of the image without extension
    :param pixels: The list of pixels as a numpy array
    :param interpolation_method: The pixels interpolation method, used for metadata
    :param pixel_size: The size of pixels, in voltage, used for metadata
    :param filter_extreme: Allow or not to filter the derived images
    """

    # Create directories if necessary
    file_dir.mkdir(parents=True, exist_ok=True)

    # Save interpolated raw image as file
    plt.imsave(file_dir / f'{file_basename}.png', pixels, cmap='Greys', metadata={
        'interpolation_method': interpolation_method,
        'pixel_size': f'{pixel_size:.6f}V',
    })

    # Compute the gradient with respect to each dimension
    pixels_gradient = np.gradient(pixels)

    if filter_extreme:
        # Limit pixel values between the 1st and 99th percentile to avoid visual issues with extreme values
        for pixel_d in pixels_gradient:
            percentile1 = np.percentile(pixel_d, 1)
            percentile99 = np.percentile(pixel_d, 99)
            pixel_d[np.where(pixel_d < percentile1)] = percentile1
            pixel_d[np.where(pixel_d > percentile99)] = percentile99

    # Save interpolated gradient by x image as file
    plt.imsave(file_dir / f'{file_basename}_DzDx.png', pixels_gradient[1], cmap='Greens', metadata={
        'interpolation_method': interpolation_method,
        'pixel_size': f'{pixel_size:.6f}V',
        'derivative_method': 'numpy.gradient',
        'type_of_derived': 'by x',
    })

    # Save interpolated gradient by y image as file
    plt.imsave(file_dir / f'{file_basename}_DzDy.png', pixels_gradient[0], cmap='Blues', metadata={
        'interpolation_method': interpolation_method,
        'pixel_size': f'{pixel_size:.6f}V',
        'derivative_method': 'numpy.gradient',
        'type_of_derived': 'by y',
    })


def save_interpolated_csv(file_path: Path, values, x, y, pixel_size: float) -> None:
    """
    Save interpolated data as a CSV file.

    :param file_path: The path where to save the CSV. The extension define the file format (GZ or CSV)
    :param values: The list of voltage values as a numpy array
    :param x: The x coordinates of the pixels (post interpolation), used in information row
    :param y: The y coordinates of the pixels (post interpolation), used in information row
    :param pixel_size: The size of pixels, in voltage, used in information row
    """
    # Create directories if necessary
    file_path.parent.mkdir(parents=True, exist_ok=True)

    compact_diagram = np.insert(values, 0, [x[0][0], y[0][0], pixel_size] + [0] * (len(x[0]) - 3), 0)
    np.savetxt(file_path, compact_diagram, delimiter=',', fmt='%.6g',
               header='First row: x start (V), y start (V), step (V) / Second row to end: values (V)')


def load_interpolated_csv(file_path: Union[IO, str, Path]) -> Tuple:
    """
    Load the stability diagrams from CSV file.

    :param file_path: The path to the CSV file or the byte stream.
    :return: The stability diagram data as a tuple: x, y, values
    """
    compact_diagram = np.loadtxt(file_path, delimiter=',')
    # Extract information
    x_start, y_start, step = compact_diagram[0][0], compact_diagram[0][1], compact_diagram[0][2]

    # Remove the information row
    values = np.delete(compact_diagram, 0, 0)

    # Reconstruct the axes

    x = np.arange(values.shape[1]) * step + x_start
    y = np.arange(values.shape[0]) * step + y_start

    return x, y, values


def main():
    label = DatasetLabel(settings.api_key) if settings.upload_images else None
    raw_clean_dir = Path(OUT_DIR, 'raw_clean')
    img_out_dir = Path(OUT_DIR, 'interpolated_img', f'{settings.pixel_size * 1000}mV')
    csv_out_dir = Path(OUT_DIR, 'interpolated_csv', f'{settings.pixel_size * 1000}mV')

    count = 0
    skipped = 0

    for diagram_file in raw_clean_dir.rglob('*.csv'):
        # Plot a specific area of the diagram
        focus_area = None
        # focus_area = (-0.460, -0.440, -0.65, -0.63)

        # Compute out file paths
        file_basename = diagram_file.stem  # Remove extension
        current_csv_dir = csv_out_dir / diagram_file.parent.relative_to(raw_clean_dir)  # Keep the file structure
        current_img_dir = img_out_dir / diagram_file.parent.relative_to(raw_clean_dir)  # Keep the file structure
        out_csv_file = current_csv_dir / f'{file_basename}.gz'

        # If the csv file exists, skip everything (no image created)
        if out_csv_file.is_file():
            skipped += 1
            continue

        # Load data
        diagram = pandas.read_csv(diagram_file)

        if settings.plot_results:
            # Plot raw points
            plot_raw(diagram, file_basename, focus_area, grid_size=None)

        # Interpolate
        x_i, y_i, pixels = image_interpolation(diagram,
                                               method=settings.interpolation_method,
                                               step=settings.pixel_size,
                                               filter_extreme=False)

        # Save interpolated values
        current_csv_dir.mkdir(parents=True, exist_ok=True)
        save_interpolated_csv(out_csv_file, pixels, x_i, y_i, settings.pixel_size)

        if settings.filter_extreme:
            _, _, pixels = image_interpolation(diagram,
                                               method=settings.interpolation_method,
                                               step=settings.pixel_size,
                                               filter_extreme=True)

        del diagram  # Explicite remove large data
        gc.collect()

        if settings.plot_results:
            # Plot the image
            plot_image(x_i, y_i, pixels, file_basename, settings.interpolation_method, settings.pixel_size,
                       focus_area=focus_area)

        # Save the interpolated image and derived images
        save_images(current_img_dir, file_basename, pixels, settings.interpolation_method,
                    settings.pixel_size)

        # Upload image into Labelbox
        if settings.upload_images:
            label.load_img_into_labelbox(current_img_dir, file_basename)

        count += 1

        del pixels  # Explicite remove large data
        gc.collect()

    print(f'{count} raw file(s) interpolated')
    if skipped > 0:
        print(f'{skipped} file(s) skipped (already existing)')


if __name__ == '__main__':
    # Show the current settings
    print(settings)

    # Processing settings at the top of this file
    main()
