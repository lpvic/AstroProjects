from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.stats import biweight_midvariance


stats_formulas = {'MIN': lambda x: np.min(x),
                  'MAX': lambda x: np.max(x),
                  'AVG': lambda x: np.average(x),
                  'MED': lambda x: np.median(x),
                  'STD': lambda x: np.std(x),
                  'VAR': lambda x: np.var(x),
                  'MAD': lambda x: np.median(np.absolute(x - np.median(x))),  # Median Absolute Deviation (MAD)
                  'SBW': lambda x: np.sqrt(biweight_midvariance(x)),  # Square Root of Biweight Midvariance
                  'AAD': lambda x: np.mean(np.absolute(x - np.mean(x)))}  # Average Absolute Deviation (AAD)


def calculate_stats(fits_file: Path) -> dict:
    out = {}
    with fits.open(fits_file) as fin:
        header = fin[0].header
        if abs(header['BITPIX']) == 16:
            data = fin[0].data
        elif abs(header['BITPIX']) == 32:
            data = np.round(fin[0].data * 65535).astype('int64')

    if header['NAXIS'] == 2:
        for k, v in stats_formulas.items():
            out[k] = v(data)

    elif header['NAXIS'] == 3:
        for channel in range(3):
            out[channel] = {k: v(data[channel, :, :]) for k, v in stats_formulas.items()}

    return out


def create_stats_hdu(stats: dict) -> fits.BinTableHDU:
    col_name = fits.Column(name='NAME', format='3A', array=np.array(stats.keys()))
    col_value = fits.Column(name='VALUE', format='E', array=np.array(stats.values()))

    return fits.BinTableHDU.from_columns([col_name, col_value])
