from pathlib import Path
from datetime import datetime, timedelta
from dateutil import tz

from astropy.io import fits


def update_fits_fields(file: Path, new_data: dict) -> None:
    with fits.open(file, mode='update') as fits_file:
        header = fits_file[0].header
        for field in list(new_data.keys()):
            header[field] = new_data[field]


def get_fields_from_foldername(foldername: Path) -> dict:
    out = {}
    fields = foldername.name.split('_')
    out['IMAGETYP'] = fields[0].title()

    cameras = {'294MC': 'ZWO ASI294MC Pro', '174MM': 'ZWO ASI174MM Mini'}
    if out['IMAGETYP'] == 'Dark':
        fields[5] = cameras[fields[5]]
        out = {**out, 'SESSION': int(fields[1]), 'SEQUENCE': int(fields[2]), 'EXPTIME': float(fields[3][:-2]) / 1000.,
               'XBINNING': int(fields[4][3:]), 'INSTRUME': fields[5], 'GAIN': int(fields[6][4:]),
               'SET-TEMP': float(fields[7][:-1])}
    elif out['IMAGETYP'] == 'Flat':
        fields[5] = cameras[fields[5]]
        out = {**out, 'SESSION': int(fields[1]), 'SEQUENCE': int(fields[2]),
               'EXPTIME': float(fields[3][:-2]) / 1000., 'XBINNING': int(fields[4][3:]), 'INSTRUME': fields[5],
               'FILTER': fields[6], 'GAIN': int(fields[7][4:]), 'SET-TEMP': float(fields[8][:-1])}
    elif out['IMAGETYP'] == 'Light':
        fields[6] = cameras[fields[6]]
        out = {**out, 'OBJECT': fields[1], 'SESSION': int(fields[2]), 'SEQUENCE': int(fields[3]),
               'EXPTIME': float(fields[4][:-2]) / 1000., 'XBINNING': int(fields[5][3:]), 'INSTRUME': fields[6],
               'FILTER': fields[7], 'GAIN': int(fields[8][4:]), 'SET-TEMP': float(fields[9][:-1])}

    return out


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
                if field == 'SEQUENCE':
                    out[field] = 0
                else:
                    out[field] = ''

    return out


def get_foldername(d: dict) -> str:
    if 'dark' in d['IMAGETYP']:
        return (d['IMAGETYP'].title() + '_' + '{:0>8d}'.format(int(d['SESSION'])) + '_' +
                '{:0>2d}'.format(int(d['SEQUENCE'])) + '_' + '{:0>8.1f}'.format(1000.0 * d['EXPTIME']) + 'ms' + '_' +
                'Bin' + '{:0>1d}'.format(d['XBINNING']) + '_' + d['INSTRUME'][7:12] + '_' + 'Gain' +
                '{:0>3d}'.format(d['GAIN']) + '_' + str(float(d['SET-TEMP'])) + 'C')
    elif 'flat' in d['IMAGETYP']:
        return (d['IMAGETYP'].title() + '_' + '{:0>8d}'.format(int(d['SESSION'])) + '_' +
                '{:0>2d}'.format(int(d['SEQUENCE'])) + '_' + '{:0>8.1f}'.format(1000.0 * d['EXPTIME']) + 'ms' + '_' +
                'Bin' + '{:0>1d}'.format(d['XBINNING']) + '_' + d['INSTRUME'][7:12] + '_' +
                d['FILTER'].replace(' ', '') + '_' + 'Gain' + '{:0>3d}'.format(d['GAIN']) + '_' +
                str(float(d['SET-TEMP'])) + 'C')
    elif 'light' in d['IMAGETYP']:
        return (d['IMAGETYP'].title() + '_' + d['OBJECT'].replace(' ', '') + '_' + '{:0>8d}'.format(int(d['SESSION'])) +
                '_' + '{:0>2d}'.format(int(d['SEQUENCE'])) + '_' + '{:0>8.1f}'.format(1000.0 * d['EXPTIME']) + 'ms' +
                '_' + 'Bin' + '{:0>1d}'.format(d['XBINNING']) + '_' + d['INSTRUME'][7:12] + '_' +
                d['FILTER'].replace(' ', '') + '_' + 'Gain' + '{:0>3d}'.format(d['GAIN']) + '_' +
                str(float(d['SET-TEMP'])) + 'C')


def get_filename(d: dict) -> str:
    out = get_foldername(d)
    return out + '_' + '{:0>5d}'.format(d['FRAME']) + '.fit'


def get_session(date_obs: str, exptime: float, frame: int) -> str:
    try:
        dt = datetime.strptime(date_obs, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        return '19000101'

    dt = dt.replace(tzinfo=tz.gettz('UTC'))
    dt = dt.astimezone(tz.gettz('Europe/Madrid'))
    dt = dt.replace(tzinfo=None)
    if (dt - timedelta(seconds=(frame - 1) * exptime)).hour < 12:
        return datetime.strftime(dt - timedelta(days=1), '%Y%m%d')
    else:
        return (dt - timedelta(seconds=(frame - 1) * exptime)).strftime('%Y%m%d')
