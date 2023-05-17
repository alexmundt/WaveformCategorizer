# WaveformCategorizer
This repo contains python code for categorizing waveforms quickly.

## Needed packages
- numpy
- matplotlib
- scipy
- tqdm
- obspy
- pandas 

## Usage
To use run

```
python run.py
```

The `run.py` file contains options for the maximum frequency to use in the plot of the Fourier spectra as well as for the folder containing the waveforms.

```
# mseed files to read are in the folder
folder_name = "example data"
# the maximum frequency to be displayed in the Fourier domain
max_freq = 0.9
```

Supported waveform files are in `.mseed`-format. The files are expected to end in a 8-character unique event ID code.


## Categorizing waveforms
After pressing the `keyboard navigation mode` button the interface will react to several keyboard prompts:
- `q` for switching between the categories
- `1` to `5` for different quality levels
- `Left` and `Right` arrow keys for switching between waveforms quickly

The `Save` and `Load` buttons will either store the current categorizations in a pandas pickle file.


# Example image
<picture>
 <img src="example_usage.png">
</picture>
