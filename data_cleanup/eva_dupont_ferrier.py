from pathlib import Path
from typing import IO, List, Tuple
from zipfile import ZipFile

import numpy as np
import pandas as pd

from raw_to_images import plot_raw


def load_raw_points(diagram_file: IO) -> Tuple[List[float], List[float], List]:
    """
    Load the raw files with all columns.

    :param diagram_file: The diagram file to load.
    :return: The columns x, y, z according to the selected ones.
    """
    data = np.loadtxt(diagram_file)
    x = data[:, 0]
    y = data[:, 2]
    z = data[:, 4]
    return x, y, z


if __name__ == '__main__':
    count = 0
    is_double_dot = {'20221103-160513_Map_B3_D3', '20221103-144107_Map_B3_D3', '20221103-104426_Map_B3_D3',
                     '20210702-115629_MAP_G1_G3', '20210630-095228_MAP_G1_G3', '20210618-174008_Map_G1_G3',
                     '20210617-181617_Map_G1_G3', '20210616-184118_Map_G1_G3', '20210604-195344_Map_G1_G3',
                     '20210604-172616_Map_G1_G3', '20210604-143253_Map_G1_G3', '20210603-231408_Map_G1_G3',
                     '20210506-175351_Map_G1_G3', '20210428-005851_Map_G1_G3', '20210427-170907_Map_G1_G3',
                     '20210427-091957_Map_G1_G3', '20210427-001016_Map_G1_G3', '20220618-121944_Map_B4_D3_highres',
                     '20220702-095838_Map_D3_D2', '20220703-143147_Map_D3_D2', '20221130-180708_Map_D2_D1'}
    with ZipFile('../data/originals/eva_dupont_ferrier.zip', 'r') as zip_file:
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
                f'../out/raw_clean/{"double" if (file_name[:-4] in is_double_dot) else "single"}/eva_dupont_ferrier')
            out_dir.mkdir(parents=True, exist_ok=True)
            df.to_csv(out_dir / f'{file_name[:-4]}.csv', index=False)
            count += 1

    print(f'{count} raw diagrams converted to csv')
