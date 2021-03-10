from pathlib import Path
from typing import List, Tuple, Union
from zipfile import ZipFile

import numpy as np
import pandas as pd
from typing.io import IO

from raw_to_images import plot_raw


def load_raw_points(file_path: Union[IO, str, Path]) -> Tuple[List[float], List[float], List]:
    """
    Load the raw files with all columns (some are useless the game is to find which ones)

    :param file_path: The path to the dataset to load
    :return: The columns x, y, z according to the selected ones.
    """
    # Read file
    data = np.genfromtxt(file_path, delimiter=',', skip_footer=1)
    # Chose the columns
    return data[:, 3], data[:, 1], data[:, 5]


if __name__ == '__main__':
    file = 'jul25300s'
    with ZipFile('../../data/originals/louis_gaudreau.zip', 'r') as zip_file:
        x, y, values = load_raw_points(zip_file.open(file + '.grey'))

    df = pd.DataFrame({'x': x, 'y': y, 'z': values})
    plot_raw(df, file)

    print(df)
    print(df.describe(percentiles=[.25, .5, .75, .99]))
    df.to_csv(f'../../out/louis_clean/louis_gaudreau_{file}.csv', index=False)
