import os
from datetime import datetime, timedelta
from dateutil import tz

import pandas as pd

from io_utils import mkdir, mv, get_file_list
from fits_utils import update_fits_fields, get_fields_from_fits


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

fields_ordered = ['ASIFILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SEQUENCE', 'FRAME', 'INSTRUME', 'FILTER',
                  'EXPOSURE', 'XBINNING', 'GAIN', 'SET-TEMP', 'GUIDECAM', 'MOUNT', 'TELESCOP', 'LENS', 'FOCALLEN',
                  'OBJECT', 'OBSERVER',  'SITENAME', 'SITELAT', 'SITELON', 'NEWFOLD', 'NEWFILE']


def update_dict(source_dict: dict, new_values: dict) -> dict:
    for k, v in new_values.items():
        source_dict[k] = v
    return source_dict


def get_fields_from_foldername(foldername: str) -> dict:
    out = {}
    fields = os.path.basename(foldername).split('_')
    out['IMAGETYP'] = fields[0].title()

    if out['IMAGETYP'] == 'Dark':
        if fields[5] == '294MC':
            fields[5] = 'ZWO ASI294MC Pro'
        elif fields[5] == '174MM':
            fields[5] = 'ZWO ASI174MM Mini'
        out = {**out, 'SESSION': int(fields[1]), 'SEQUENCE': int(fields[2]), 'EXPOSURE': float(fields[3][:-2]) / 1000.,
               'XBINNING': int(fields[4][3:]), 'INSTRUME': fields[5], 'GAIN': int(fields[6][4:]),
               'SET-TEMP': float(fields[7][:-1])}
    elif out['IMAGETYP'] == 'Flat':
        if fields[5] == '294MC':
            fields[5] = 'ZWO ASI294MC Pro'
        elif fields[5] == '174MM':
            fields[5] = 'ZWO ASI174MM Mini'
        out = {**out, 'SESSION': int(fields[1]), 'SEQUENCE': int(fields[2]),
               'EXPOSURE': float(fields[3][:-2]) / 1000., 'XBINNING': int(fields[4][3:]), 'INSTRUME': fields[5],
               'FILTER': fields[6], 'GAIN': int(fields[7][4:]), 'SET-TEMP': float(fields[8][:-1])}
    elif out['IMAGETYP'] == 'Light':
        if fields[6] == '294MC':
            fields[6] = 'ZWO ASI294MC Pro'
        elif fields[6] == '174MM':
            fields[6] = 'ZWO ASI174MM Mini'
        out = {**out, 'OBJECT': fields[1], 'SESSION': int(fields[2]), 'SEQUENCE': int(fields[3]),
               'EXPOSURE': float(fields[4][:-2]) / 1000., 'XBINNING': int(fields[5][3:]), 'INSTRUME': fields[6],
               'FILTER': fields[7], 'GAIN': int(fields[8][4:]), 'SET-TEMP': float(fields[9][:-1])}

    return out


def initialize_folders(from_folder: str) -> None:
    darks = os.path.join(from_folder, os.path.normpath(r'sources/darks'))
    flats = os.path.join(from_folder, os.path.normpath(r'sources/flats'))
    lights = os.path.join(from_folder, os.path.normpath(r'sources/lights'))
    master_darks = os.path.join(from_folder, os.path.normpath(r'masters/darks'))
    master_flats = os.path.join(from_folder, os.path.normpath(r'masters/flats'))
    projects = os.path.join(from_folder, os.path.normpath(r'projects'))

    if not os.path.isdir(darks):
        mkdir(darks)
    if not os.path.isdir(flats):
        mkdir(flats)
    if not os.path.isdir(lights):
        mkdir(lights)
    if not os.path.isdir(master_darks):
        mkdir(master_darks)
    if not os.path.isdir(master_flats):
        mkdir(master_flats)
    if not os.path.isdir(projects):
        mkdir(projects)


def get_between(value: int, intervals: tuple) -> int:
    for i in intervals:
        if (value >= i[0]) and (value <= i[1]):
            return i

    raise ValueError('Value out of range')


def get_telescope(focal: int) -> str:

    teles = {(250, 290): 'Askar V60', (350, 370): 'Askar V60',  (430, 460): 'Askar V60',
             (371, 410): 'Askar V80', (475, 525): 'Askar V80', (570, 630): 'Askar V80',
             (2000, 3000): 'Celestron EdgeHD 800', (1300, 1600): 'Celestron EdgeHD 800',
             (10, 150): 'Nikon AF-S DX Nikkor 18-140mm f/3.5-5.6G ED VR'}

    return teles[get_between(focal, list(teles.keys()))]


def get_lens(focal: int) -> str:
    lens = {(250, 290): '0.75x', (350, 370): '1.00x', (430, 460): '1.24x',
            (371, 410): '0.78x', (475, 525): '1.00x', (570, 630): '1.21x',
            (2000, 3000): '1.00x', (1300, 1600): '0.7x',
            (10, 150): '1.00x'}

    return lens[get_between(focal, list(lens.keys()))]


def is_astrofile(filename: str) -> bool:
    return (filename.endswith('.fit') and
            (filename.startswith('Light') or filename.startswith('Dark') or filename.startswith('Flat')))


def create_foldername(d: dict) -> str:
    if d['IMAGETYP'] == 'Dark':
        return (d['IMAGETYP'].lower() + '_' + '{:0>8d}'.format(int(d['SESSION'])) + '_' +
                '{:0>2d}'.format(int(d['SEQUENCE'])) + '_' + '{:0>8.1f}'.format(1000.0 * d['EXPOSURE']) + 'ms' + '_' +
                'Bin' + str(d['XBINNING']) + '_' + d['INSTRUME'][7:12] + '_' + 'gain' + str(d['GAIN']) + '_' +
                str(float(d['SET-TEMP'])) + 'C')

    elif d['IMAGETYP'] == 'Flat':
        return (d['IMAGETYP'].lower() + '_' + '{:0>8d}'.format(int(d['SESSION'])) + '_' +
                '{:0>2d}'.format(int(d['SEQUENCE'])) + '_' + '{:0>8.1f}'.format(1000.0 * d['EXPOSURE']) + 'ms' + '_' +
                'Bin' + str(d['XBINNING']) + '_' + d['INSTRUME'][7:12] + '_' + d['FILTER'].replace(' ', '') + '_' +
                'gain' + str(d['GAIN']) + '_' + str(float(d['SET-TEMP'])) + 'C')
    elif d['IMAGETYP'] == 'Light':
        return (d['IMAGETYP'].lower() + '_' + d['OBJECT'].replace(' ', '') + '_' + '{:0>8d}'.format(int(d['SESSION'])) +
                '_' + '{:0>2d}'.format(int(d['SEQUENCE'])) + '_' + '{:0>8.1f}'.format(1000.0 * d['EXPOSURE']) + 'ms' +
                '_' + 'Bin' + str(d['XBINNING']) + '_' + d['INSTRUME'][7:12] + '_' + d['FILTER'].replace(' ', '') +
                '_' + 'gain' + str(d['GAIN']) + '_' + str(float(d['SET-TEMP'])) + 'C')


def create_filename(d: dict) -> str:
    out = create_foldername(d)
    return out + '_' + '{:0>5d}'.format(d['FRAME']) + '.fit'


def create_fits_import_list(from_folder: str, to_folder: str) -> None:
    folders = [x[0] for x in os.walk(from_folder)]
    filename_list = [x[2] for x in os.walk(from_folder)]

    df0 = pd.DataFrame()
    if os.path.exists(os.path.join(to_folder, r'asiair_imported_files.csv')):
        df0 = pd.read_csv(os.path.join(to_folder, r'asiair_imported_files.csv'), sep=';', na_values=['NaN'],
                          keep_default_na=False)
        db = df0.to_dict('records')
    else:
        db = []

    fields = ['IMAGETYP', 'FOCALLEN', 'SET-TEMP', 'XBINNING', 'EXPOSURE', 'DATE-OBS', 'FILTER', 'INSTRUME', 'GUIDECAM',
              'GAIN', 'TELESCOP', 'OBJECT', 'LENS']

    counter = 1
    for folder, filenames in zip(folders, filename_list):
        for filename in filenames:
            original_file = os.path.relpath(os.path.join(folder, filename), from_folder)

            if not df0.empty:
                if original_file in df0['ASIFILE'].values:
                    continue

            if is_astrofile(filename) and os.path.getsize(os.path.join(folder, filename)) != 0:
                data = get_fields_from_fits(os.path.join(from_folder, original_file), fields_ordered)
                try:
                    frame_num = int(filename[:-4].split('_')[-1])
                except ValueError:
                    continue

                data = update_dict(data, {'ASIFILE': original_file,
                                          'OBSERVER': 'Luis Pedro Vicente Matilla', 'MOUNT': 'ZWO AM5',
                                          'SITENAME': 'Otero de Bodas, Spain', 'SITELAT': '41 56 17 N',
                                          'SITELON': '06 09 03 W', 'FRAME': frame_num})

                try:
                    dt = datetime.strptime(data['DATE-OBS'], '%Y-%m-%dT%H:%M:%S.%f')
                except ValueError:
                    continue

                dt = dt.replace(tzinfo=tz.gettz('UTC'))
                dt = dt.astimezone(tz.gettz('Europe/Madrid'))
                dt = dt.replace(tzinfo=None)
                if (dt - timedelta(seconds=(int(data['FRAME']) - 1) * data['EXPOSURE'])).hour < 12:
                    data['SESSION'] = datetime.strftime(dt - timedelta(days=1), '%Y%m%d')
                else:
                    data['SESSION'] = (dt - timedelta(
                        seconds=(int(data['FRAME']) - 1) * data['EXPOSURE'])).strftime('%Y%m%d')

                if data['IMAGETYP'] == 'Dark':
                    data = update_dict(data, {'FOCALLEN': '', 'TELESCOP': '', 'GUIDECAM': '', 'FILTER': '',
                                              'MOUNT': '', 'SITENAME': '', 'SITELAT': '', 'SITELON': ''})
                elif data['IMAGETYP'] == 'Flat':
                    data = update_dict(data, {'TELESCOP': get_telescope(data['FOCALLEN']),
                                              'LENS': get_lens(data['FOCALLEN']), 'GUIDECAM': '',
                                              'FILTER': 'Unk' if data['FILTER'] == '' else data['FILTER'], 'MOUNT': '',
                                              'SITENAME': '', 'SITELAT': '', 'SITELON': ''})
                elif data['IMAGETYP'] == 'Light':
                    data = update_dict(data, {'TELESCOP': get_telescope(data['FOCALLEN']),
                                              'LENS': get_lens(data['FOCALLEN']),
                                              'OBJECT': filename.split('_')[1].replace(' ', ''),
                                              'FILTER': 'Unk' if data['FILTER'] == '' else data['FILTER']})

                db.append(data)
                counter = counter + 1

    sorted_db = sorted(db, key=lambda d: d['DATE-OBS'])
    sorted_db[0]['SEQUENCE'] = 1
    sorted_db[0]['NEWFOLD'] = create_foldername(sorted_db[0])
    sorted_db[0]['NEWFILE'] = create_filename(sorted_db[0])
    seq = 1
    for i in range(1, len(sorted_db)):
        if sorted_db[i]['SESSION'] != sorted_db[i - 1]['SESSION']:
            seq = 1
        elif sorted_db[i]['FRAME'] <= sorted_db[i - 1]['FRAME']:
            seq = seq + 1
        sorted_db[i]['SEQUENCE'] = seq
        sorted_db[i]['NEWFOLD'] = create_foldername(sorted_db[i])
        sorted_db[i]['NEWFILE'] = create_filename(sorted_db[i])

    df = pd.DataFrame(sorted_db)
    df = df[fields_ordered]
    df.to_csv(os.path.join(to_folder, r'asiair_imported_files.csv'), sep=';', index=False)


def import_fits(from_folder: str, to_folder: str, import_file: str = 'asiair_imported_files.csv') -> None:
    sub_folders = {'Dark': r'sources\darks', 'Flat': r'sources\flats', 'Light': r'sources/lights'}
    df_import = pd.read_csv(os.path.join(to_folder, import_file), sep=';', na_values=['NaN'], keep_default_na=False)

    flog = open(os.path.join(to_folder, 'moved.log'), 'w')

    for idx, row in df_import.iterrows():
        src_file = os.path.join(from_folder, row['ASIFILE'])
        dst_folder = os.path.join(to_folder, sub_folders[row['IMAGETYP']], row['NEWFOLD'])
        dst_file = os.path.join(dst_folder, row['NEWFILE'])

        if not os.path.exists(src_file):
            continue

        if not os.path.exists(dst_folder):
            mkdir(dst_folder)

        if not os.path.exists(dst_file):
            mv(src_file, dst_file)
            update_fits_fields(dst_file, row.to_dict())
            flog.write(src_file + ' -> ' + dst_file + '\n')
    flog.close()


def apply_corrections(in_folder: str, corrections_file: str) -> None:
    sub_folders = {'Dark': r'sources\darks', 'Flat': r'sources\flats', 'Light': r'sources/lights'}
    df_corrections = pd.read_csv(os.path.join(in_folder, corrections_file), sep=';', na_values=['NaN'],
                            keep_default_na=False)

    for idx, row in df_corrections.iterrows():
        img_type = row['NEWFOLD'].split('_')[0].title()
        dst_folder = os.path.join(in_folder, sub_folders[img_type], row['NEWFOLD'])

        if not os.path.exists(dst_folder):
            continue

        file_list = get_file_list(dst_folder, row['NEWFOLD'])
        changed_fields = row.to_dict()
        for k in list(changed_fields.keys()):
            if changed_fields[k] == '':
                del changed_fields[k]
        new_fields = {**get_fields_from_foldername(dst_folder), **changed_fields}
        new_fields['NEWFOLD'] = create_foldername(new_fields)

        for file in file_list:
            file_fields = get_fields_from_fits(file, fields_ordered)
            new_fields['FRAME'] = file_fields['FRAME']
            new_fields['NEWFILE'] = create_filename(new_fields)
            update_fits_fields(file, new_fields)
            mv(file, os.path.join(dst_folder, new_fields['NEWFILE']))
        os.rename(dst_folder, os.path.join(in_folder, sub_folders[img_type], new_fields['NEWFOLD']))
