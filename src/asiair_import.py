from pathlib import Path
from datetime import datetime, timedelta
from dateutil import tz

import pandas as pd

from src.fits_utils import update_fits_fields, get_fields_from_fits, get_session
from src.gen_utils import update_dict, get_between
from src.database import db_fields


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


def initialize_folders(from_folder: Path) -> None:
    (from_folder / r'sources/darks').mkdir(parents=True, exist_ok=True)
    (from_folder / r'sources/flats').mkdir(parents=True, exist_ok=True)
    (from_folder / r'sources/lights').mkdir(parents=True, exist_ok=True)
    (from_folder / r'masters/darks').mkdir(parents=True, exist_ok=True)
    (from_folder / r'masters/flats').mkdir(parents=True, exist_ok=True)
    (from_folder / r'projects').mkdir(parents=True, exist_ok=True)


def get_telescope(focal: int) -> str:

    teles = {(250, 290): 'Askar V60', (350, 370): 'Askar V60',  (430, 460): 'Askar V60',
             (371, 410): 'Askar V80', (475, 525): 'Askar V80', (570, 630): 'Askar V80',
             (2000, 3000): 'Celestron EdgeHD 800', (1300, 1600): 'Celestron EdgeHD 800',
             (10, 150): 'Nikon AF-S DX Nikkor 18-140mm f/3.5-5.6G ED VR'}

    return teles[get_between(focal, list(teles.keys()))] if focal > 0 else 0


def get_lens(focal: int) -> str:
    lens = {(250, 290): '0.75x', (350, 370): '1.00x', (430, 460): '1.24x',
            (371, 410): '0.78x', (475, 525): '1.00x', (570, 630): '1.21x',
            (2000, 3000): '1.00x', (1300, 1600): '0.7x',
            (10, 150): '1.00x'}

    return lens[get_between(focal, list(lens.keys()))]


def update_database(asiair_folder: Path, astroprojects_folder: Path, image_type: str) -> None:
    img_type = image_type.lower()
    db_path = astroprojects_folder / ('asiair_' + img_type + '_table.csv')
    if db_path.exists():
        db = pd.read_csv(db_path, sep=';')
    else:
        db = pd.DataFrame(columns=db_fields[img_type])

    for file in asiair_folder.rglob(img_type.title() + '_*.fit'):
        rel_file = file.relative_to(asiair_folder)
        if (db['ASIFILE'] == rel_file).any():
            continue
        else:
            print(file)
            data = get_fields_from_fits(file, db_fields[img_type])

            additional_data = {
                'dark': {'FOCALLEN': 0, 'TELESCOP': '', 'GUIDECAM': '', 'FILTER': '', 'MOUNT': '', 'SITENAME': '',
                         'SITELAT': '', 'SITELON': ''},
                'flat': {'TELESCOP': get_telescope(data['FOCALLEN']), 'LENS': get_lens(data['FOCALLEN']),
                         'GUIDECAM': '', 'FILTER': 'Unk' if data['FILTER'] == '' else data['FILTER'], 'MOUNT': '',
                         'SITENAME': '', 'SITELAT': '', 'SITELON': ''},
                'light': {'TELESCOP': get_telescope(data['FOCALLEN']), 'LENS': get_lens(data['FOCALLEN']),
                          'OBJECT': file.stem.split('_')[1].replace(' ', ''),
                          'FILTER': 'Unk' if data['FILTER'] == '' else data['FILTER']}
            }

            data = update_dict(data, additional_data[img_type])
            data = update_dict(data, {
                'FRAME': int(file.stem.split('_')[-1]),
                'SESSION': get_session(data['DATE-OBS'], data['EXPTIME'], int(file.stem.split('_')[-1])),
                'ASIFILE': rel_file, 'OBSERVER': 'Luis Pedro Vicente Matilla', 'MOUNT': 'ZWO AM5',
                'SITENAME': 'Otero de Bodas, Spain', 'SITELAT': '41 56 17 N', 'SITELON': '06 09 03 W'})


            print(data)
