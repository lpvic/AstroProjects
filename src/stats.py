from astropy.io import fits
import numpy as np


if __name__ == '__main__':
    with fits.open(r'/nas/sdm1/AstroProjects/masters/darks/master_dark_20240731_03_004500.0ms_bin1_294MC_gain120_-10.0C.fit') as fits_file:
        header = fits_file[0].header
        data = fits_file[0].data
    print(header)
    print(np.max(data))
    print(np.min(data))
    print(np.average(data))

    with fits.open(r'/nas/sdm1/AstroProjects/sources/darks/dark_20240731_03_004500.0ms_bin1_294MC_gain120_-10.0C/dark_20240731_03_004500.0ms_bin1_294MC_gain120_-10.0C_00030.fit') as sub:
        data = sub[0].data
    print(np.max(data))
    print(np.min(data))
    print(np.average(data))
