from typing import List, Tuple
from zipfile import ZipFile

import numpy as np
import pandas as pd
from typing.io import IO

from raw_to_images import plot_raw


def load_raw_points(file: IO) -> Tuple[List[float], List[float], List]:
    """
    Load the raw files with all columns (some are useless the game is to find which ones
    Function based on this notebook (private link) :
    https://usherbrooke-my.sharepoint.com/:u:/r/personal/roum2013_usherbrooke_ca/Documents/Doctorat/Data/Data%20set%20for%20machine%20learning/data_info.ipynb?csf=1&web=1&e=BOvoam

    :param file: The diagram file to load.
    :return: The columns x, y, z according to the selected ones.
    """

    # Reading .dat file
    file_content = file.readlines()

    # Reading header
    header_size = 0
    param_labels = ["Sweep channel: Name", "Sweep channel: Start", "Sweep channel: Stop", "Sweep channel: Points",
                    "Step channel 1: Name", "Step channel 1: Start", "Step channel 1: Stop", "Step channel 1: Points",
                    "Acquire channels"]
    params = dict.fromkeys(param_labels)
    for line in file_content:
        line = line.decode()  # bytes to str

        for label in param_labels:
            if label in line:
                if "Name" in label:
                    params[label] = line.split("\t")[1]
                elif "Points" in label:
                    params[label] = int(float(line.split("\t")[1]))
                elif "Acquire channels" in label:
                    params[label] = line.split("\t")[1].split(";")
                else:
                    params[label] = float(line.split("\t")[1])

        if '[DATA]' not in line:
            header_size = header_size + 1
        else:
            header_size = header_size + 2  # skip [DATA] line and column labels
            break

    print(params)

    # Extract data from file
    data = np.genfromtxt(file_content[header_size:]).transpose()
    data = data[1:, :]  # first row is the x-axis, remove from data

    # Separate data measured from multiple channels
    nb_ch = len(params["Acquire channels"])
    data_arrays = []
    for ch in range(nb_ch):
        data_arrays.append(data[ch::nb_ch])

    # Verify shape of data
    data_shape = data_arrays[0].shape  # (y length, x length)
    header_data_shape = (params["Step channel 1: Points"], params["Sweep channel: Points"])

    if data_shape != header_data_shape:  # if the measurement is incomplete for example
        # Adjust y-axis last point
        dy = (params["Step channel 1: Stop"] - params["Step channel 1: Start"]) / (params["Step channel 1: Points"])
        params["Step channel 1: Stop"] = params["Step channel 1: Start"] + dy * data_shape[0]

        # Adjust number of points
        params["Step channel 1: Points"], params["Sweep channel: Points"] = data_shape

    # Reconstruct axis from header
    x = np.linspace(params["Sweep channel: Start"], params["Sweep channel: Stop"], params["Sweep channel: Points"])
    y = np.linspace(params["Step channel 1: Start"], params["Step channel 1: Stop"], params["Step channel 1: Points"])

    # Process data for all channels measured
    for i in range(nb_ch):
        z = data_arrays[i]
        if "Demod" not in params["Acquire channels"][i]:
            dz = np.gradient(z, axis=1)  # use the numerical derivative if transconductance is not used
        else:
            dz = z

        # Flatten image
        len_y, len_x = z.shape
        z = z.reshape(-1)
        # Match axis with flatten image
        x = x.reshape((1, -1)).repeat(len_y, axis=0).reshape(-1)
        y = y.repeat(len_x)

        # Return only the first channel
        return x, y, z


if __name__ == '__main__':

    count = 0

    # TODO check why "1779Dev2-20161127_473.dat" is not good
    not_valid = ['1779Dev2-20161127_473.dat']

    with ZipFile('../../data/originals/michel_pioro_ladriere.zip', 'r') as zip_file:
        for file_name in zip_file.namelist():

            if file_name in not_valid:
                continue

            with zip_file.open(file_name, 'r') as file:
                x, y, values = load_raw_points(file)

            df = pd.DataFrame({'x': x, 'y': y, 'z': values})
            plot_raw(df, file_name)

            print(f'---------- {file_name[:-4]} ----------')
            print(df)
            print(df.describe(percentiles=[.25, .5, .75, .99]))

            # Change '.dat' for '.csv'
            df.to_csv(f'../../out/raw_clean/michel_pioro_ladriere_{file_name[:-4]}.csv', index=False)
            count += 1

    print(f'{count} raw diagrams converted to csv')
