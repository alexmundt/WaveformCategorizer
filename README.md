# WaveformCategorizer
This repo contains python code for categorizing waveforms quickly.

## Needed packages
- numpy
- matplotlib
- scipy
- tqdm
- obspy

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


# Example image
<picture>
 <img src="example_usage.png">
</picture>
