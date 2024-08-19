import os
from datetime import datetime, timedelta
from dateutil import tz

import pandas as pd
from astropy.io import fits

from ioutils import mkdir


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

columns_order = ['ORIG-FILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SERIES', 'SEQUENTIAL', 'INSTRUME', 'FILTER',
                 'EXPOSURE', 'XBINNING', 'GAIN', 'SET-TEMP', 'GUIDECAM', 'MOUNT', 'TELESCOP', 'LENS', 'FOCALLEN',
                 'OBJECT', 'OBSERVER',  'SITENAME', 'SITELAT', 'SITELON']


def initialize_folders(from_folder):
    darks = os.path.join(from_folder, os.path.normpath(r'Darks/sources'))
    flats = os.path.join(from_folder, os.path.normpath(r'Flats/sources'))
    lights = os.path.join(from_folder, os.path.normpath(r'Lights'))

    if not os.path.isdir(darks):
        mkdir(darks)
    if not os.path.isdir(flats):
        mkdir(flats)
    if not os.path.isdir(lights):
        mkdir(lights)


def get_between(value, intervals):
    for i in intervals:
        if (value >= i[0]) and (value <= i[1]):
            return i

    raise ValueError('Value out of range')


def get_telescope(focal):

    teles = {(250, 290): 'Askar V60', (350, 370): 'Askar V60',  (430, 460): 'Askar V60',
             (371, 410): 'Askar V80', (475, 525): 'Askar V80', (570, 630): 'Askar V80',
             (2000, 3000): 'Celestron EdgeHD 800', (1300, 1600): 'Celestron EdgeHD 800',
             (10, 150): 'Nikon AF-S DX Nikkor 18-140mm f/3.5-5.6G ED VR'}

    return teles[get_between(focal, list(teles.keys()))]


def get_lens(focal):
    lens = {(250, 290): '0.75x', (350, 370): '1.00x', (430, 460): '1.24x',
            (371, 410): '0.78x', (475, 525): '1.00x', (570, 630): '1.21x',
            (2000, 3000): '1.00x', (1300, 1600): '0.7x',
            (10, 150): '1.00x'}

    return lens[get_between(focal, list(lens.keys()))]


def is_astrofile(filename):
    return (filename.endswith('.fit') and
            (filename.startswith('Light') or filename.startswith('Dark') or filename.startswith('Flat')))


def create_filename(d):
    if d['IMAGETYP'] == 'Dark':
        pass
    elif d['IMAGETYP'] == 'Flat':
        pass
    elif d['IMAGETYP'] == 'Light':
        pass


def read_fits(from_folder):
    folders = [x[0] for x in os.walk(from_folder)]
    filename_list = [x[2] for x in os.walk(from_folder)]

    fields = ['IMAGETYP', 'FOCALLEN', 'SET-TEMP', 'XBINNING', 'EXPOSURE', 'DATE-OBS', 'FILTER', 'INSTRUME', 'GUIDECAM',
              'GAIN', 'TELESCOP', 'OBJECT', 'LENS']

    db = []
    counter = 1
    for folder, filenames in zip(folders, filename_list):
        for filename in filenames:
            if is_astrofile(filename) and os.path.getsize(os.path.join(folder, filename)) != 0:
                data = {'ORIG-FILE': os.path.relpath(os.path.join(folder, filename), from_folder),
                        'OBSERVER': 'Luis Pedro Vicente Matilla', 'MOUNT': 'ZWO AM5',
                        'SITENAME': 'Otero de Bodas, Spain', 'SITELAT': '41 56 17 N', 'SITELON': '06 09 03 W',
                        'SEQUENTIAL': filename[:-4].split('_')[-1]}
                with fits.open(os.path.join(from_folder, data['ORIG-FILE'])) as fits_file:
                    header = fits_file[0].header
                    for field in fields:
                        try:
                            data[field] = header[field]
                        except KeyError:
                            data[field] = ''

                    try:
                        dt = datetime.strptime(data['DATE-OBS'], '%Y-%m-%dT%H:%M:%S.%f')
                    except ValueError:
                        continue
                    dt = dt.replace(tzinfo=tz.gettz('UTC'))
                    dt = dt.astimezone(tz.gettz('Europe/Madrid'))
                    dt = dt.replace(tzinfo=None)
                    if (dt - timedelta(seconds=(int(data['SEQUENTIAL']) - 1) * data['EXPOSURE'])).hour < 12:
                        data['SESSION'] = datetime.strftime(dt - timedelta(days=1), '%Y%m%d')
                    else:
                        data['SESSION'] = (dt - timedelta(
                            seconds=(int(data['SEQUENTIAL']) - 1) * data['EXPOSURE'])).strftime('%Y%m%d')

                    if data['IMAGETYP'] == 'Dark':
                        data['FOCALLEN'] = ''
                        data['TELESCOP'] = ''
                        data['GUIDECAM'] = ''
                        data['FILTER'] = ''
                        data['MOUNT'] = ''
                        data['SITENAME'] = ''
                        data['SITELAT'] = ''
                        data['SITELON'] = ''
                    elif data['IMAGETYP'] == 'Flat':
                        data['TELESCOP'] = get_telescope(data['FOCALLEN'])
                        data['LENS'] = get_lens(data['FOCALLEN'])
                        data['GUIDECAM'] = ''
                        data['MOUNT'] = ''
                        data['SITENAME'] = ''
                        data['SITELAT'] = ''
                        data['SITELON'] = ''
                        if data['FILTER'] == '':
                            data['FILTER'] = 'Unk'
                    elif data['IMAGETYP'] == 'Light':
                        data['TELESCOP'] = get_telescope(data['FOCALLEN'])
                        data['LENS'] = get_lens(data['FOCALLEN'])
                        data['OBJECT'] = filename.split('_')[1]
                        if data['FILTER'] == '':
                            data['FILTER'] = 'Unk'

                db.append(data)
                print(counter)
                counter = counter + 1

    sorted_db = sorted(db, key=lambda d: d['DATE-OBS'])
    sorted_db[0]['SERIES'] = 1
    seq = 1
    for i in range(1, len(sorted_db)):
        if sorted_db[i]['SESSION'] != sorted_db[i - 1]['SESSION']:
            seq = 1
        elif sorted_db[i]['SEQUENTIAL'] <= sorted_db[i - 1]['SEQUENTIAL']:
            seq = seq + 1
        sorted_db[i]['SERIES'] = seq

    df = pd.DataFrame(db)
    df = df[columns_order]
    return df


def apply_filter_corrections():
    fits_df = pd.read_csv(os.path.join(start_folder, r'asiair_raw.csv'), sep=';', na_values=['NaN'],
                          keep_default_na=False)
    filter_df = pd.read_csv(os.path.join(start_folder, r'filter_correction.csv'), na_values=['NaN'],
                            keep_default_na=False)

    fits_df = fits_df.merge(filter_df, on='ORIG-FILE', how='left')
    fits_df['FILTER_y'] = fits_df['FILTER_y'].fillna('')
    fits_df.drop(['FILTER_x'], inplace=True, axis=1)
    fits_df.rename(columns={'FILTER_y': 'FILTER'}, inplace=True)
    fits_df = fits_df[columns_order]

    fits_df.to_csv(os.path.join(start_folder, r'asiair_import.csv'), sep=';', index=False)


if __name__ == '__main__':
    ####################################################################################################################
    start_folder = os.path.normpath(r'D:\AstroProjects')
    # initialize_folders(start_folder)
    ####################################################################################################################

    ####################################################################################################################
    # asiar_folder = os.path.normpath(r'D:\Asiair')
    #
    # fits_df = read_fits(asiar_folder)
    # fits_df.to_csv(os.path.join(start_folder, r'asiair_raw.csv'), sep=';', index=False)
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
    # fits_df[['ORIG-FILE', 'flat_folder', 'FILTER']][fits_df['IMAGETYP'] == 'Flat'].to_csv(r'..\out\flats.csv',
    #                                                                                       sep=';', index=False)
    ####################################################################################################################

    ####################################################################################################################
    # apply_filter_corrections()
    ####################################################################################################################


