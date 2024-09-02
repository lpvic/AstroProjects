from pathlib import Path

import pandas as pd

from src.utils.gen_utils import to_int, to_float

db_raw_fields = ['ASIFILE', 'NEWFILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SEQUENCE', 'FRAME', 'INSTRUME', 'FILTER',
                 'EXPTIME', 'XBINNING', 'GAIN', 'SET-TEMP', 'GUIDECAM', 'MOUNT', 'TELESCOP', 'LENS', 'FOCALLEN',
                 'OBJECT', 'OBSERVER',  'SITENAME', 'SITELAT', 'SITELON']

db_stacked_fields = ['FILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SEQUENCE', 'INSTRUME', 'FILTER',
                     'EXPTIME', 'XBINNING', 'GAIN', 'SET-TEMP', 'GUIDECAM', 'MOUNT', 'TELESCOP', 'LENS', 'FOCALLEN',
                     'OBJECT', 'AUTHOR',  'SITENAME', 'SITELAT', 'SITELON']

default_values = {'ASIFILE': '', 'NEWFILE': '', 'FILE': '', 'IMAGETYP': '', 'DATE-OBS': '', 'SESSION': '19000101',
                  'SEQUENCE': 0, 'FRAME': 0, 'INSTRUME': '', 'FILTER': 'Unk', 'EXPTIME': 0., 'XBINNING': 0, 'GAIN': -1,
                  'SET-TEMP': -99., 'GUIDECAM': '', 'MOUNT': '', 'TELESCOP': '', 'LENS': '', 'FOCALLEN': 0,
                  'OBJECT': '', 'OBSERVER': '',  'SITENAME': '', 'SITELAT': '', 'SITELON': '', 'AUTHOR': ''}

format_fields = {'ASIFILE': '{}', 'NEWFILE': '{}', 'FILE': {}, 'IMAGETYP': '{}', 'DATE-OBS': '{}', 'SESSION': '{}',
                 'SEQUENCE': '{:0>2d}', 'FRAME': '{:0>2d}', 'INSTRUME': '{}', 'FILTER': '{}',
                 'EXPTIME': '{:0>8.1f}ms', 'XBINNING': 'bin{:0>1d}', 'GAIN': 'gain{:0>3d}', 'SET-TEMP': '{:.1f}C',
                 'GUIDECAM': '{}', 'MOUNT': '{}', 'TELESCOP': '{}', 'LENS': '{}', 'FOCALLEN': '{:d}',
                 'OBJECT': '{}', 'OBSERVER': '{}',  'SITENAME': '{}', 'SITELAT': '{}', 'SITELON': '{}', 'AUTHOR': ''}


camera = {'294MC': 'ZWO ASI294MC Pro', '174MM': 'ZWO ASI174MM Mini'}
instrument = {v: k for k, v in camera.items()}


def convert(field: str, value: str | int | float) -> str | int | float:
    if field in ['ASIFILE', 'NEWFILE']:
        return Path(value)
    elif field in ['SEQUENCE', 'FRAME', 'XBINNING', 'GAIN', 'FOCALLEN']:
        return to_int(value)
    elif field in ['EXPTIME', 'SET-TEMP']:
        return to_float(value)
    else:
        return value


def read_files_database(db_path: Path) -> pd.DataFrame:
    out = pd.read_csv(db_path, sep=';', na_values='NaN', keep_default_na=False).drop_duplicates()
    for field in ['SEQUENCE', 'FRAME', 'XBINNING', 'GAIN', 'FOCALLEN', 'EXPTIME', 'SET-TEMP']:
        try:
            out[field] = pd.to_numeric(out[field], errors='coerce').fillna(default_values[field])
        except KeyError:
            continue
    for field in ['ASIFILE', 'NEWFILE', 'FILE']:
        try:
            out[field] = out[field].apply(lambda x: Path(x))
        except KeyError:
            continue

    try:
        out = out.astype({'SEQUENCE': 'int64', 'FRAME': 'int64', 'XBINNING': 'int64', 'GAIN': 'int64',
                          'FOCALLEN': 'int64', 'EXPTIME': 'float64', 'SET-TEMP': 'float64'})
    except KeyError:
        out = out.astype({'SEQUENCE': 'int64', 'XBINNING': 'int64', 'GAIN': 'int64',
                          'FOCALLEN': 'int64', 'EXPTIME': 'float64', 'SET-TEMP': 'float64'})
    return out


def read_stats_database(db_path: Path) -> pd.DataFrame:
    out = pd.read_csv(db_path, sep=';', na_values='NaN', keep_default_na=False).drop_duplicates()
    for field in ['FILE']:
        try:
            out[field] = out[field].apply(lambda x: Path(x))
        except KeyError:
            continue
    return out
