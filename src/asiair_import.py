import os
from datetime import datetime, timedelta
from dateutil import tz

import pandas as pd
from astropy.io import fits

from ioutils import mkdir, move_file


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

fields_ordered = ['ASIAIRFILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SEQUENCE', 'FRAME', 'INSTRUME', 'FILTER',
                  'EXPOSURE', 'XBINNING', 'GAIN', 'SET-TEMP', 'GUIDECAM', 'MOUNT', 'TELESCOP', 'LENS', 'FOCALLEN',
                  'OBJECT', 'OBSERVER',  'SITENAME', 'SITELAT', 'SITELON', 'NEWFOLDER', 'NEWFILENAME']


def update_dict(source_dict: dict, new_values: dict) -> dict:
    for k, v in new_values.items():
        source_dict[k] = v
    return source_dict


def get_fields_from_filename(filename: str) -> dict:
    pass


def get_fields_from_fits(filename: str) -> dict:
    out = {}
    with fits.open(filename) as fits_file:
        header = fits_file[0].header
        for field in fields_ordered:
            try:
                out[field] = header[field]
            except KeyError:
                if field == 'SET-TEMP':
                    out[field] = -99.0
                else:
                    out[field] = ''

    return out


def update_fits_fields(filename: str, new_data: dict) -> None:
    with fits.open(filename) as fits_file:
        header = fits_file[0].header
        for field in list(new_data.keys()):
            header[field] = new_data[field]
        fits_file.flush()


def initialize_folders(from_folder: str) -> None:
    darks = os.path.join(from_folder, os.path.normpath(r'Darks/sources'))
    flats = os.path.join(from_folder, os.path.normpath(r'Flats/sources'))
    lights = os.path.join(from_folder, os.path.normpath(r'Lights'))

    if not os.path.isdir(darks):
        mkdir(darks)
    if not os.path.isdir(flats):
        mkdir(flats)
    if not os.path.isdir(lights):
        mkdir(lights)


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
    db = []

    fields = ['IMAGETYP', 'FOCALLEN', 'SET-TEMP', 'XBINNING', 'EXPOSURE', 'DATE-OBS', 'FILTER', 'INSTRUME', 'GUIDECAM',
              'GAIN', 'TELESCOP', 'OBJECT', 'LENS']

    counter = 1
    for folder, filenames in zip(folders, filename_list):
        for filename in filenames:
            original_file = os.path.relpath(os.path.join(folder, filename), from_folder)

            if not df0.empty:
                if original_file in df0['ASIAIRFILE'].values:
                    continue

            if is_astrofile(filename) and os.path.getsize(os.path.join(folder, filename)) != 0:
                data = get_fields_from_fits(os.path.join(from_folder, original_file))
                try:
                    frame_num = int(filename[:-4].split('_')[-1])
                except ValueError:
                    continue

                data = update_dict(data, {'ASIAIRFILE': original_file,
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
                                              'LENS': get_lens(data['FOCALLEN']), 'OBJECT': filename.split('_')[1],
                                              'FILTER': 'Unk' if data['FILTER'] == '' else data['FILTER']})

                db.append(data)
                counter = counter + 1

    sorted_db = sorted(db, key=lambda d: d['DATE-OBS'])
    sorted_db[0]['SEQUENCE'] = 1
    seq = 1
    for i in range(1, len(sorted_db)):
        print(i, sorted_db[i]['ASIAIRFILE'])
        if sorted_db[i]['SESSION'] != sorted_db[i - 1]['SESSION']:
            seq = 1
        elif sorted_db[i]['FRAME'] <= sorted_db[i - 1]['FRAME']:
            seq = seq + 1
        sorted_db[i]['SEQUENCE'] = seq
        sorted_db[i]['NEWFOLDER'] = create_foldername(sorted_db[i])
        sorted_db[i]['NEWFILENAME'] = create_filename(sorted_db[i])

    df = pd.DataFrame(db)
    df = df[fields_ordered]
    df.to_csv(os.path.join(to_folder, r'asiair_imported_files.csv'), sep=';', index=False)


def apply_corrections(to_folder) -> None:
    fits_df = pd.read_csv(os.path.join(to_folder, r'asiair_raw.csv'), sep=';', na_values=['NaN'],
                          keep_default_na=False)
    filter_df = pd.read_csv(os.path.join(to_folder, r'filter_correction.csv'), na_values=['NaN'],
                            keep_default_na=False)

    object_df = pd.read_csv(os.path.join(to_folder, r'object_correction.csv'), na_values=['NaN'],
                            keep_default_na=False)

    fits_df = fits_df.merge(filter_df, on='ASIAIRFILE', how='left')
    fits_df['FILTER_y'] = fits_df['FILTER_y'].fillna('')
    fits_df.drop(['FILTER_x'], inplace=True, axis=1)
    fits_df.rename(columns={'FILTER_y': 'FILTER'}, inplace=True)
    fits_df = fits_df[fields_ordered]

    fits_df = fits_df.merge(object_df, on='ASIAIRFILE', how='left')
    fits_df['OBJECT_y'] = fits_df['OBJECT_y'].fillna('')
    fits_df.drop(['OBJECT_x'], inplace=True, axis=1)
    fits_df.rename(columns={'OBJECT_y': 'OBJECT'}, inplace=True)
    fits_df = fits_df[fields_ordered]

    fits_df.to_csv(os.path.join(to_folder, r'asiair_import.csv'), sep=';', index=False)


def import_file():
    pass


if __name__ == '__main__':
    ####################################################################################################################
    dest_folder = os.path.normpath(r'D:\AstroProjects')
    asiar_folder = os.path.normpath(r'D:\Asiair')
    initialize_folders(dest_folder)
    create_fits_import_list(asiar_folder, dest_folder)
    ####################################################################################################################

    ####################################################################################################################
    # fits_df = pd.read_csv('../out/asiair_raw.csv', sep=';', na_values=['NaN'], keep_default_na=False)
    # fits_df = fits_df[fits_df['INSTRUME'] == 'ZWO ASI294MC Pro']
    # fits_df['flat_folder'] = (fits_df['IMAGETYP'].str.lower() + '_' + fits_df['SESSION'].astype(str) + '_' +
    #                           fits_df['EXPOSURE'].apply(lambda x: '{:0>8.1f}'.format(1000.0 * x)) + 'ms' +
    #                           '_Bin' + fits_df['XBINNING'].astype(str) + '_' + fits_df['INSTRUME'].str[7:12] + '_' +
    #                           fits_df['FILTER'].str.replace(' ', '') + '_gain' + fits_df['GAIN'].astype('str') + '_' +
    #                           fits_df['SET-TEMP'].astype('float').astype(str) + 'C')
    #
    # print(len(fits_df['flat_folder'][(fits_df['IMAGETYP'] == 'Flat') & (fits_df['FILTER'] == 'Unk')].unique()))
    # fits_df[['ASIAIRFILE', 'flat_folder', 'FILTER']][fits_df['IMAGETYP'] == 'Flat'].to_csv(r'..\out\flats.csv',
    #                                                                                       sep=';', index=False)
    ####################################################################################################################

    ####################################################################################################################
    # apply_corrections()
    ####################################################################################################################
