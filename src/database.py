from pathlib import Path

import pandas as pd

from src.gen_utils import to_int, to_float

db_raw_fields = ['ASIFILE', 'NEWFILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SEQUENCE', 'FRAME', 'INSTRUME', 'FILTER',
                 'EXPTIME', 'XBINNING', 'GAIN', 'SET-TEMP', 'GUIDECAM', 'MOUNT', 'TELESCOP', 'LENS', 'FOCALLEN',
                 'OBJECT', 'OBSERVER',  'SITENAME', 'SITELAT', 'SITELON']

db_stacked_fields = ['FILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SEQUENCE', 'INSTRUME', 'FILTER',
                     'EXPTIME', 'XBINNING', 'GAIN', 'SET-TEMP', 'GUIDECAM', 'MOUNT', 'TELESCOP', 'LENS', 'FOCALLEN',
                     'OBJECT', 'AUTHOR',  'SITENAME', 'SITELAT', 'SITELON']

default_values = {'ASIFILE': '', 'NEWFILE': '', 'IMAGETYP': '', 'DATE-OBS': '', 'SESSION': '19000101', 'SEQUENCE': 0,
                  'FRAME': 0, 'INSTRUME': '', 'FILTER': '', 'EXPTIME': 0., 'XBINNING': 0, 'GAIN': -1,
                  'SET-TEMP': -99., 'GUIDECAM': '', 'MOUNT': '', 'TELESCOP': '', 'LENS': '', 'FOCALLEN': 0,
                  'OBJECT': '', 'OBSERVER': '',  'SITENAME': '', 'SITELAT': '', 'SITELON': '', 'AUTHOR': ''}

format_fields = {'ASIFILE': '{}', 'NEWFILE': '{}', 'IMAGETYP': '{}', 'DATE-OBS': '{}', 'SESSION': '{}',
                 'SEQUENCE': '{:0>2d}', 'FRAME': '{:0>2d}', 'INSTRUME': '{}', 'FILTER': '{}',
                 'EXPTIME': '{:0>8.1f}ms', 'XBINNING': 'Bin{:0>1d}', 'GAIN': 'Gain{:0>3d}', 'SET-TEMP': '{:.1f}C',
                 'GUIDECAM': '{}', 'MOUNT': '{}', 'TELESCOP': '{}', 'LENS': '{}', 'FOCALLEN': '{:d}',
                 'OBJECT': '{}', 'OBSERVER': '{}',  'SITENAME': '{}', 'SITELAT': '{}', 'SITELON': '{}', 'AUTHOR': ''}


camera = {'294MC': 'ZWO ASI294MC Pro', '174MM': 'ZWO ASI174MM Mini'}
instrument = {v: k for k, v in camera.items()}


def convert(field: str, value: str | int | float) -> str | int | float:
    if field in ['ASIFILE', 'NEWFILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'INSTRUME', 'FILTER', 'GUIDECAM', 'MOUNT',
                 'TELESCOP', 'LENS', 'OBJECT', 'OBSERVER', 'AUTHOR', 'SITENAME', 'SITELAT', 'SITELON']:
        return value
    elif field in ['SEQUENCE', 'FRAME', 'XBINNING', 'GAIN', 'FOCALLEN']:
        return to_int(value)
    elif field in ['EXPTIME', 'SET-TEMP']:
        return to_float(value)


def read_asiair_database(db_path: Path) -> pd.DataFrame:
    out = pd.read_csv(db_path, sep=';', na_values='NaN', keep_default_na=False).drop_duplicates()
    for field in ['SEQUENCE', 'FRAME', 'XBINNING', 'GAIN', 'FOCALLEN', 'EXPTIME', 'SET-TEMP']:
        out[field] = pd.to_numeric(out[field], errors='coerce').fillna(default_values['field'])

    return out
