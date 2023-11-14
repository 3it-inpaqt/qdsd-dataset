from pathlib import Path
from typing import List, Tuple, Union, IO
from zipfile import ZipFile

import numpy as np
import pandas as pd

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
    # We expect the format as x, y, z or x1 x2 y z1 z2 (but only one z contains diagram values)
    return data[:, 3], data[:, 1], data[:, 5] * 1e-12  # Values are in pA


if __name__ == '__main__':
    # The file have to be process one by one because the column format are not always the same
    file = 'jul25300s'
    with ZipFile('../data/originals/louis_gaudreau.zip', 'r') as zip_file:
        x, y, values = load_raw_points(zip_file.open(file + '.grey'))

    df = pd.DataFrame({'x': x, 'y': y, 'z': values})
    plot_raw(df, file)

    print(df)
    print(df.describe(percentiles=[.25, .5, .75, .99]))

    # Save CSV file
    out_dir = Path(f'../out/raw_clean/louis_gaudreau/')
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / f'{file}.csv', index=False)
