from pathlib import Path

import numpy
import numpy as np
from astropy.io import fits
from astropy.stats import biweight_midvariance

from src.utils.gen_utils import update_dict

from scipy.signal import argrelextrema
from matplotlib import pyplot as plt
from scipy.stats import mode


stats_formulas = {'MIN': lambda x: np.min(x),
                  'MAX': lambda x: np.max(x),
                  'AVG': lambda x: np.average(x),
                  'MED': lambda x: np.median(x),
                  'STD': lambda x: np.std(x),
                  'VAR': lambda x: np.var(x),
                  'MAD': lambda x: np.median(np.absolute(x - np.median(x))),  # Median Absolute Deviation (MAD)
                  'SBW': lambda x: np.sqrt(biweight_midvariance(x)),  # Square Root of Biweight Midvariance
                  'AAD': lambda x: np.mean(np.absolute(x - np.mean(x))),  # Average Absolute Deviation (AAD)
                  'BGN': 9999999}  # Reserved for background noise calculation


def calculate_stats(fits_file: Path) -> list:
    out = []
    channels_rgb = ['R', 'G', 'B']

    with fits.open(fits_file) as fin:
        header = fin[0].header
        if abs(header['BITPIX']) == 16:
            data = fin[0].data
        elif abs(header['BITPIX']) == 32:
            data = np.round(fin[0].data * 65535).astype('int64')

    if header['NAXIS'] == 2:
        st = {'CHANNEL': 'BW'}
        st = update_dict(st, {k: v(data) for k, v in stats_formulas.items()})
        out.append(st)

    elif header['NAXIS'] == 3:
        for channel in range(3):
            st = {'CHANNEL': channels_rgb[channel]}
            st = update_dict(st, {k: v(data[channel, :, :]) for k, v in stats_formulas.items()})
            out.append(st)

    return out


def create_stats_hdu(stats: dict) -> fits.BinTableHDU:
    col_name = fits.Column(name='NAME', format='3A', array=np.array(stats.keys()))
    col_value = fits.Column(name='VALUE', format='E', array=np.array(stats.values()))

    return fits.BinTableHDU.from_columns([col_name, col_value])


def moving_average(a, n=2):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n
