import gzip
import json
import zipfile
from pathlib import Path
from typing import Iterable, List, Tuple

from shapely.geometry import LineString, Polygon

from plots import plot_image
from raw_to_images import load_interpolated_csv

DATA_DIR = Path('data')
PIXEL_SIZE = 0.0010  # Volt
SINGLE_DOT = True  # If false take double dot
RESEARCH_GROUP = 'michel_pioro_ladriere'  # 'louis_gaudreau' or 'michel_pioro_ladriere'


def clip(n, smallest, largest):
    """ Shortcut to clip a value between 2 others """
    return max(smallest, min(n, largest))


def coord_to_volt(coord: Iterable[float], min_coord: int, max_coord: int, value_start: float, value_step: float,
                  snap: int = 1, is_y: bool = False) -> List[float]:
    """
    Convert some coordinates to volt value for a specific stability diagram.

    :param coord: The list coordinates to convert
    :param min_coord: The minimal valid value for the coordinate (before volt conversion)
    :param max_coord: The maximal valid value for the coordinate (before volt conversion)
    :param value_start: The voltage value of the 0 coordinate
    :param value_step: The voltage difference between two coordinates (pixel size)
    :param snap: The snap margin, every points near to image border at this distance will be rounded to the image border
    (in number of pixels)
    :param is_y: If true this is the y axis (to apply a rotation)
    :return: The list of coordinates as gate voltage values
    """
    if is_y:
        # Flip Y axis (I don't know why it's required)
        coord = list(map(lambda t: max_coord - t, coord))

    # Snap to border to avoid errors
    coord = list(map(lambda t: clip(t, min_coord, max_coord), coord))

    # Convert coordinates to actual voltage value
    coord = list(map(lambda t: t * value_step + value_start, coord))

    return coord


def load_charge_annotations(charge_areas: Iterable, x, y, snap: int = 1) -> List[Tuple[str, Polygon]]:
    """
    Load regions annotation for an image.

    :param charge_areas: List of charge area label as json object (from Labelbox export)
    :param x: The x axis of the diagram (in volt)
    :param y: The y axis of the diagram (in volt)
    :param snap: The snap margin, every points near to image border at this distance will be rounded to the image border
    (in number of pixels)
    :return: The list of regions annotation for the image, as (label, shapely.geometry.Polygon)
    """

    # Define borders for snap
    min_x, max_x = 0, len(x) - 1
    min_y, max_y = 0, len(y) - 1
    # Step (should be the same for every measurement)
    step = x[1] - x[0]

    processed_areas = []
    for area in charge_areas:
        area_x = coord_to_volt((p['x'] for p in area['polygon']), min_x, max_x, x[0], step, snap)
        area_y = coord_to_volt((p['y'] for p in area['polygon']), min_y, max_y, y[0], step, snap, True)

        area_obj = Polygon(zip(area_x, area_y))
        processed_areas.append((area['value'], area_obj))

    return processed_areas


def load_lines_annotations(lines: Iterable, x, y, snap: int = 1) -> List[LineString]:
    """
    Load transition line annotations for an image.

    :param lines: List of line label as json object (from Labelbox export)
    :param x: The x axis of the diagram (in volt)
    :param y: The y axis of the diagram (in volt)
    :param snap: The snap margin, every points near to image border at this distance will be rounded to the image border
    (in number of pixels)
    :return: The list of line annotation for the image, as shapely.geometry.LineString
    """

    # Define borders for snap
    min_x, max_x = 0, len(x) - 1
    min_y, max_y = 0, len(y) - 1
    # Step (should be the same for every measurement)
    step = x[1] - x[0]

    processed_lines = []
    for line in lines:
        line_x = coord_to_volt((p['x'] for p in line['line']), min_x, max_x, x[0], step, snap)
        line_y = coord_to_volt((p['y'] for p in line['line']), min_y, max_y, y[0], step, snap, True)

        line_obj = LineString(zip(line_x, line_y))
        processed_lines.append(line_obj)

    return processed_lines


def main():
    # Open the json file that contains annotations for every diagrams
    with open(Path(DATA_DIR, 'labels.json'), 'r') as annotations_file:
        labels_json = json.load(annotations_file)

    print(f'{len(labels_json)} labeled diagrams found')
    labels = {obj['External ID']: obj for obj in labels_json}

    # Open the zip file and iterate over all csv files
    zip_path = Path(DATA_DIR, 'interpolated_csv.zip')
    in_zip_path = Path(f'{PIXEL_SIZE * 1000}mV', 'single' if SINGLE_DOT else 'double', RESEARCH_GROUP)
    zip_dir = zipfile.Path(zip_path, str(in_zip_path) + '/')

    if not zip_dir.is_dir():
        raise ValueError(f'Folder "{in_zip_path}" not found in the zip file "{zip_path}"')

    for diagram_name in zip_dir.iterdir():
        file_basename = Path(str(diagram_name)).stem  # Remove extension

        if f'{file_basename}.png' not in labels:
            print(f'No label found for {file_basename}')
            continue

        with diagram_name.open('r') as diagram_file:
            # Load values from CSV file
            x, y, values = load_interpolated_csv(gzip.open(diagram_file))

            current_labels = labels[f'{file_basename}.png']['Label']['objects']

            # Load annotation and convert the coordinates to volt
            transition_lines = load_lines_annotations(filter(lambda l: l['title'] == 'line', current_labels), x, y,
                                                      snap=1)
            charge_regions = load_charge_annotations(filter(lambda l: l['title'] != 'line', current_labels), x, y,
                                                     snap=1)

            plot_image(x, y, values, file_basename, 'nearest', x[1] - x[0], charge_regions, transition_lines)


if __name__ == '__main__':
    # Processing settings at the top of this file
    main()
