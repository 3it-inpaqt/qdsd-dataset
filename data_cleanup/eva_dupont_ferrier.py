import re
from pathlib import Path
from typing import List, Tuple
from zipfile import ZipFile

import numpy as np
import pandas as pd
from typing.io import IO

from raw_to_images import plot_raw


def load_raw_points(file: IO) -> Tuple[List[float], List[float], List]:
    """
    Load the raw files with all columns.

    :param file: The diagram file to load.
    :return: The columns x, y, z according to the selected ones.
    """

    amplification = None
    for line in file:
        line = line.decode("utf-8")
        match = re.match(r'.*:= Ampli(?:fication)?[=:](.+)$', line)
        if match:
            amplification = int(float(match[1]))  # Parse exponential notation to integer
            break
        if line[0] != '#':
            raise RuntimeError('Amplification value not found in file comments')

    print(f'Amplification: {amplification}')
    data = np.loadtxt(file)
    x = data[:, 0]
    y = data[:, 2]
    z = data[:, 4]
    return x, y, z


if __name__ == '__main__':
    count = 0
    is_double_dot = ['20220618-121944_Map_B4_D3_highres', '20220702-095838_Map_D3_D2', '20220703-143147_Map_D3_D2']
    with ZipFile('../data/originals/eva_dupont_ferrier_gen3.zip', 'r') as zip_file:
        for file_name in zip_file.namelist():
            print(f'---------- {file_name[:-4]} ----------')
            with zip_file.open(file_name, 'r') as file:
                x, y, values = load_raw_points(file)

            df = pd.DataFrame({'x': x, 'y': y, 'z': values})
            plot_raw(df, file_name)

            print(df)
            print(df.describe(percentiles=[.25, .5, .75, .99]))

            # Change '.dat' for '.csv'
            out_dir = Path(
                f'../out/raw_clean/{"double" if (file_name[:-4] in is_double_dot) else "single"}/eva_dupont_ferrier_gen3')
            out_dir.mkdir(parents=True, exist_ok=True)
            df.to_csv(out_dir / f'{file_name[:-4]}.csv', index=False)
            count += 1

    print(f'{count} raw diagrams converted to csv')
