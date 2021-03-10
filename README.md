# Quantum Dots Stability Diagrams (QDSD) dataset

Dataset of quantum dots stability diagrams for machine learning application.

# Download data

Before public release, the data are available
in [this private Teams folder](https://usherbrooke.sharepoint.com/:f:/r/sites/UdeS-UW-Memristor-basedMLforQuantumTechs/Documents%20partages/General/Datasets/QDSD?csf=1&web=1&e=YtBFnn)
.

You need download this folder and unzip in into a `data` folder at the root of this project.

The folder is organised as:

> __originals/__ - the original data as we received it (before any processing), classed by origin.  
__raw_clean.zip__ - compressed file containing all data, each CSV file is a stability diagram. The CSV have 3 columns: `x, y, z`. Where `x` and `y` are the gate tension in V and `z` is the measured tension in V.

# Removed diagrams

Some unusable original stability diagrams were removed during the cleaning process:

* louis_gaudreau
  * jul25300s: the voltage range of `x` axes is too small
  * jul29100s: the voltage range of `x` axes is too small

# Data contribution

* Louis Gaudreau
