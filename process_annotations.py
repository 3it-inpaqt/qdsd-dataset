import gzip
import json
from pathlib import Path
from typing import List, Tuple
from zipfile import ZipFile

from raw_to_images import load_interpolated_csv, plot_image

DATA_DIR = Path('data')


def clip(n, smallest, largest):
    """ Shortcut to clip a value between 2 others """
    return max(smallest, min(n, largest))


def load_charge_annotations(annotations_json, image_name: str, x, y, snap: int = 1) -> List[Tuple[str, List, List]]:
    """
    Load regions annotation for an image.

    :param annotations_json: The json file containing all annotations.
    :param image_name: The name of the image (should match with the name in the annotation file)
    :param x: The x axis of the diagram (in volt)
    :param y: The y axis of the diagram (in volt)
    :param snap: The snap margin, every points near to image border at this distance will be rounded to the image border
    (in number of pixels)
    :return: The list of regions annotation for the image, as (label, list of x points, list of y points)
    """

    if image_name not in annotations_json:
        raise RuntimeError(f'"{image_name}" annotation not found')

    annotation_json = annotations_json[image_name]

    # Define borders for snap
    min_x, max_x = 0, len(x) - 1
    min_y, max_y = 0, len(y) - 1
    # Step (should be the same for every measurement)
    step = x[1] - x[0]

    regions = []

    for region in annotation_json['regions'].values():
        x_r = region['shape_attributes']['all_points_x']
        y_r = region['shape_attributes']['all_points_y']
        label_r = region['region_attributes']['label']

        # Close regions
        x_r.append(x_r[-1])
        y_r.append(y_r[-1])

        # Flip Y axis (I don't know why it's required)
        y_r = list(map(lambda t: max_y - t, y_r))

        # Snap to border to avoid errors
        x_r = list(map(lambda t: clip(t, min_x, max_x), x_r))
        y_r = list(map(lambda t: clip(t, min_y, max_y), y_r))

        # Convert coordinates to actual values range
        x_r = list(map(lambda t: t * step + x[0], x_r))
        y_r = list(map(lambda t: t * step + y[0], y_r))

        regions.append((label_r, x_r, y_r))

    return regions


def main():
    # Open the json file that can contain annotations for every diagrams
    with open(Path(DATA_DIR, 'charge_area.json'), 'r') as annotations_file:
        annotations_json = json.load(annotations_file)

    # Open the zip file and iterate over all csv files
    with ZipFile(Path(DATA_DIR, 'interpolated_csv.zip'), 'r') as zip_file:
        for diagram_name in zip_file.namelist():
            file_basename = Path(diagram_name).stem  # Remove extension
            with zip_file.open(diagram_name) as diagram_file:
                # Load values from CSV file
                x, y, values = load_interpolated_csv(gzip.open(diagram_file))

                diagram_annotations = load_charge_annotations(annotations_json, f'{file_basename}.png', x, y, snap=1)

                plot_image(x, y, values, file_basename, 'nearest', x[1] - x[0], diagram_annotations)
                break


if __name__ == '__main__':
    # Processing settings at the top of this file
    main()
