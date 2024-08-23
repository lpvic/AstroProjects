from pathlib import Path

from astropy.io import fits


def update_fits_fields(file: Path, new_data: dict) -> None:
    with fits.open(file, mode='update') as fits_file:
        header = fits_file[0].header
        for field in list(new_data.keys()):
            header[field] = new_data[field]


def get_fields_from_fits(file: Path, fields: list) -> dict:
    out = {}
    with fits.open(file, mode='readonly') as fits_file:
        header = fits_file[0].header
        for field in fields:
            try:
                out[field] = header[field]
            except KeyError:
                if field == 'SET-TEMP':
                    out[field] = -99.0
                else:
                    out[field] = ''

    return out
