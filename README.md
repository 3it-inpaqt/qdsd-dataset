# Quantum Dots Stability Diagrams (QDSD) dataset

Dataset of quantum dots stability diagrams for machine learning application.

# Download data

Before public release, the data are available
in [this private Teams folder](https://usherbrooke.sharepoint.com/:f:/r/sites/UdeS-UW-Memristor-basedMLforQuantumTechs/Documents%20partages/General/Datasets/QDSD?csf=1&web=1&e=YtBFnn)
.

You need download this folder and unzip in into a `data` folder at the root of this project.

The folder is organised as:

* __originals/__ - The original data as we received it (before any processing), classed by origin.  
  No data processing applied.
* __raw_clean.zip__ - Compressed files containing all data, each CSV file is a stability diagram. The CSV have 3
  columns: `x, y, z`. Where `x` and `y` are the gate tension in V and `z` is the measured tension in V.  
  No data processing applied.
* __interpolated_csv.zip__ - Compressed files containing all diagrams as CSV 2D arrays.  
  Interpolation and rounding applied (data loss).
* __interpolated_images.zip__ - Compressed files containing all diagrams as PNG images. This is mainly used to manually
  labeled the dataset.  
  Interpolation and extreme values filter applied (data loss).
* __labels.json__ - Line and charge area labels (exported from [Labelbox](https://labelbox.com/))

# Data processing

The data processing is kept minimal to be as close as possible to the reality of experimentation. However, in some case
the alteration of data was necessary to be adapted to machine learning applications.

![Process flow](doc/process_flow.svg?sanitize=true)

## Interpolation

It is necessary to have the same constant voltage variation between measurements in every stability diagrams. So we use
the 'nearest' interpolation method to upscale or downscale the resolution of the `x` or `y` axes when it was necessary.

The choice of the 'nearest' interpolation instead of 'linear' or other type of interpolation is motivated by the idea to
not smooth the values and keeping the original variability.

In the current version, the standard voltage variation is `2.5mV`.

## Filter extreme values

To visually represent the diagrams it was necessary to remove extreme values.

This was done by limiting the values between the 1st and the 99th percentile for each diagram.

## Rounding

In some case the voltage value is rounded to 6 decimals (microvolt).

# Removed diagrams

Some unusable original stability diagrams were removed during the cleaning process:

* louis_gaudreau
  * jul25300s: the voltage range of `x` axis is too small
  * jul29100s: the voltage range of `x` axis is too small
  * sep03010s: no line found

# Processing Scripts

* __data_cleanup/__: originals => raw_clean  
  Convert the specific file structure to a standard one.
* __raw_to_images/__: raw_clean => interpolated_csv & interpolated_images  
  Interpolate data to have plottable images ready to be annotated.

# Annotation tool

[Labelbox](https://labelbox.com/)

# Data contribution

* Louis Gaudreau's research group (https://doi.org/10.1063/1.3258663)
* Michel Pioro Ladriere research group
