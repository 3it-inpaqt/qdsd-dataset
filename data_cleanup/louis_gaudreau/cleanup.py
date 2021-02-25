from pathlib import Path
from typing import List, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_raw_points(file_path: Union[str, Path]) -> Tuple[List[float], List[float], List]:
    """
    Load the raw files with all columns (some are useless the game is to find which ones)

    :param file_path: The path to the dataset to load
    :return: The columns x, y, z according to the selected ones.
    """
    # Read file
    data = np.genfromtxt(file_path, delimiter=',', skip_footer=1)
    # Chose the columns
    return data[:, 1], data[:, 0], data[:, 3]


def plot_raw_image(x, y, values, image_name: str) -> None:
    """
    Plot the raw data points.
    """

    # Count unique to know the image size.
    nb_x = len(np.unique(x))
    nb_y = len(np.unique(y))

    # Reshape to the image size.
    x = x.reshape(nb_x, nb_y)
    y = y.reshape(nb_x, nb_y)
    values = values.reshape(nb_x, nb_y)

    # Plot it (with limited values to avoid extremes values issues)
    plt.pcolormesh(x, y, values, cmap='copper', shading='auto', vmax=3, vmin=-3)
    plt.title(f'{image_name} - raw')
    plt.show()


if __name__ == '__main__':
    file = 'jul29100s'
    x, y, values = load_raw_points(f'../../data/originals/louis_gaudreau/{file}.grey')

    plot_raw_image(x, y, values, file)

    df = pd.DataFrame({'x': x, 'y': y, 'z': values})
    print(df)
    print(df.describe(percentiles=[.25, .5, .75, .99]))
    df.to_csv(f'../../raw/louis_clean/louis_gaudreau_{file}.csv', index=False)
