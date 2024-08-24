from pathlib import Path
from datetime import datetime, timedelta
from dateutil import tz

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
                if field == 'SEQUENCE':
                    out[field] = 0
                else:
                    out[field] = ''

    return out


def get_foldername(d: dict) -> str:
    if 'dark' in d['IMAGETYP']:
        return (d['IMAGETYP'].lower() + '_' + '{:0>8d}'.format(int(d['SESSION'])) + '_' +
                '{:0>2d}'.format(int(d['SEQUENCE'])) + '_' + '{:0>8.1f}'.format(1000.0 * d['EXPTIME']) + 'ms' + '_' +
                'bin' + '{:0>1d}'.format(d['XBINNING']) + '_' + d['INSTRUME'][7:12] + '_' + 'g' + '{:0>3d}'.format(d['GAIN']) + '_' +
                str(float(d['SET-TEMP'])) + 'C')
    elif 'flat' in d['IMAGETYP']:
        return (d['IMAGETYP'].lower() + '_' + '{:0>8d}'.format(int(d['SESSION'])) + '_' +
                '{:0>2d}'.format(int(d['SEQUENCE'])) + '_' + '{:0>8.1f}'.format(1000.0 * d['EXPTIME']) + 'ms' + '_' +
                'bin' + '{:0>1d}'.format(d['XBINNING']) + '_' + d['INSTRUME'][7:12] + '_' + d['FILTER'].replace(' ', '') + '_' +
                'gain' + '{:0>3d}'.format(d['GAIN']) + '_' + str(float(d['SET-TEMP'])) + 'C')
    elif 'light' in d['IMAGETYP']:
        return (d['IMAGETYP'].lower() + '_' + d['OBJECT'].replace(' ', '') + '_' + '{:0>8d}'.format(int(d['SESSION'])) +
                '_' + '{:0>2d}'.format(int(d['SEQUENCE'])) + '_' + '{:0>8.1f}'.format(1000.0 * d['EXPTIME']) + 'ms' +
                '_' + 'bin' + '{:0>1d}'.format(d['XBINNING']) + '_' + d['INSTRUME'][7:12] + '_' + d['FILTER'].replace(' ', '') +
                '_' + 'gain' + '{:0>3d}'.format(d['GAIN']) + '_' + str(float(d['SET-TEMP'])) + 'C')


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
