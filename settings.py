import argparse
from dataclasses import asdict, dataclass

import configargparse
from numpy.distutils.misc_util import is_sequence


@dataclass(init=False, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class Settings:
    """
    Storing all settings for this program with default values.
    Setting are loaded from (last override first):
        - default values (in this file)
        - local file (default path: ./settings.yaml)
        - environment variables
        - arguments of the command line (with "--" in front)
    """

    # API key required for logging in labelbox
    api_key: str = ''

    # Enable or not to upload into labelbox
    upload_images: bool = False

    # Specified in which dataset the image is upload
    # If empty, we will try to fetch the dataset with the name
    dataset_id: str = ''

    # Dataset name for new dataset or to fetch an existing one
    dataset_name: str = 'Default'

    # The pixel size in volt, for the interpolation
    pixel_size: float = 0.0010

    # The interpolation method
    # See https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html
    interpolation_method: str = 'nearest'

    # The relative path to the data directory, from the working directory
    data_dir: str = 'data'

    # The relative path to the output directory, from the working directory
    out_dir: str = 'out'

    # If True, the extreme data points are removed from the generated images. But kept in the csv files.
    # The data is capped to the first and last percentile.
    filter_extreme: bool = True

    # If True, plot the diagrams as images at different steps of the processing.
    plot_results: bool = True

    def __init__(self):
        """
        Create the setting object.
        """
        self._load_file_and_cmd()

    def _load_file_and_cmd(self) -> None:
        """
        Load settings from local file and arguments of the command line.
        """

        def str_to_bool(arg_value: str) -> bool:
            """
            Used to handle boolean settings.
            If not the 'bool' type convert all not empty string as true.

            :param arg_value: The boolean value as a string.
            :return: The value parsed as a string.
            """
            if isinstance(arg_value, bool):
                return arg_value
            if arg_value.lower() in {'false', 'f', '0', 'no', 'n'}:
                return False
            elif arg_value.lower() in {'true', 't', '1', 'yes', 'y'}:
                return True
            raise argparse.ArgumentTypeError(f'{arg_value} is not a valid boolean value')

        def type_mapping(arg_value):
            if type(arg_value) == bool:
                return str_to_bool
            if is_sequence(arg_value):
                if len(arg_value) == 0:
                    return str
                else:
                    return type_mapping(arg_value[0])

            # Default same as current value
            return type(arg_value)

        p = configargparse.get_argument_parser(default_config_files=['./settings.yaml'])

        # Spacial argument
        p.add_argument('-s', '--settings', required=False, is_config_file=True,
                       help='path to custom configuration file')

        # Create argument for each attribute of this class
        for name, value in asdict(self).items():
            p.add_argument(f'--{name.replace("_", "-")}',
                           f'--{name}',
                           dest=name,
                           required=False,
                           action='append' if is_sequence(value) else 'store',
                           type=type_mapping(value))

        # Load arguments form file, environment and command line to override the defaults
        for name, value in vars(p.parse_args()).items():
            if name == 'settings':
                continue
            if value is not None:
                # Directly set the value to bypass the "__setattr__" function
                self.__dict__[name] = value

    def __setattr__(self, name, value) -> None:
        """
        Set an attribute and valide the new value.

        :param name: The name of the attribut
        :param value: The value of the attribut
        """
        if name not in self.__dict__ or self.__dict__[name] != value:
            print(f'Setting "{name}" changed from "{getattr(self, name)}" to "{value}".')
            self.__dict__[name] = value

    def __delattr__(self, name):
        raise AttributeError('Removing a setting is forbidden for the sake of consistency.')

    def __str__(self) -> str:
        """
        :return: Human readable description of the settings.
        """
        return 'Settings:\n\t' + \
            '\n\t'.join(
                [f'{name}: {"*****" if name == "api_key" else str(value)}' for name, value in asdict(self).items()])


# Singleton setting object
settings = Settings()
