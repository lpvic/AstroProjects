from pathlib import Path
from datetime import datetime, timedelta
from dateutil import tz

from astropy.io import fits

from src.database import default_values, format_fields, camera, instrument


def update_fits_fields(file: Path, new_data: dict) -> None:
    with fits.open(file, mode='update') as fits_file:
        header = fits_file[0].header
        for field in list(new_data.keys()):
            try:
                header[field] = new_data[field]
            except ValueError:
                header[field] = str(new_data[field])


def get_fields_from_foldername(foldername: Path) -> dict:
    out = {}
    fields = foldername.name.split('_')
    out['IMAGETYP'] = fields[0].lower()

    if out['IMAGETYP'] == 'dark':
        fields[5] = camera[fields[5]]
        out = {**out, 'SESSION': fields[1], 'SEQUENCE': int(fields[2]), 'EXPTIME': float(fields[3][:-2]) / 1000.,
               'XBINNING': int(fields[4][3:]), 'INSTRUME': fields[5], 'GAIN': int(fields[6][4:]),
               'SET-TEMP': float(fields[7][:-1])}
    elif out['IMAGETYP'] == 'flat':
        fields[5] = camera[fields[5]]
        out = {**out, 'SESSION': fields[1], 'SEQUENCE': int(fields[2]),
               'EXPTIME': float(fields[3][:-2]) / 1000., 'XBINNING': int(fields[4][3:]), 'INSTRUME': fields[5],
               'FILTER': fields[6], 'GAIN': int(fields[7][4:]), 'SET-TEMP': float(fields[8][:-1])}
    elif out['IMAGETYP'] == 'light':
        fields[6] = camera[fields[6]]
        out = {**out, 'OBJECT': fields[1], 'SESSION': fields[2], 'SEQUENCE': int(fields[3]),
               'EXPTIME': float(fields[4][:-2]) / 1000., 'XBINNING': int(fields[5][3:]), 'INSTRUME': fields[6],
               'FILTER': fields[7], 'GAIN': int(fields[8][4:]), 'SET-TEMP': float(fields[9][:-1])}

    return out


def get_fields_from_fits(file: Path, fields: list) -> dict:
    out = {}

    with fits.open(file, mode='readonly') as fits_file:
        header = fits_file[0].header
        for field in fields:
            try:
                if field == 'IMAGETYP':
                    out[field] = header[field].lower()
                else:
                    out[field] = header[field]
            except KeyError:
                out[field] = default_values[field]

    return out


def get_raw_foldername(d: dict) -> str:
    fullname = [format_fields['IMAGETYP'].format(d['IMAGETYP']).replace(' ', '').lower(),
                format_fields['OBJECT'].format(d['OBJECT']).replace(' ', ''),
                format_fields['SESSION'].format(d['SESSION']),
                format_fields['SEQUENCE'].format(d['SEQUENCE']),
                format_fields['EXPTIME'].format(1000 * d['EXPTIME']),
                format_fields['XBINNING'].format(d['XBINNING']),
                format_fields['INSTRUME'].format(instrument[d['INSTRUME']]),
                format_fields['FILTER'].format(d['FILTER']),
                format_fields['GAIN'].format(d['GAIN']),
                format_fields['SET-TEMP'].format(d['SET-TEMP']),
                ]
    fields = {'dark': [0, 2, 3, 4, 5, 6, 8, 9],
           'flat': [0, 2, 3, 4, 5, 6, 7, 8, 9],
           'light': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}

    return '_'.join([fullname[i] for i in fields[fullname[0]]])


def get_raw_filename(d: dict) -> str:
    out = get_raw_foldername(d)
    return out + '_' + '{:0>5d}'.format(d['FRAME']) + '.fit'


def get_session(date_obs: str, exptime: float, frame: int) -> int:
    try:
        dt = datetime.strptime(date_obs, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        return 19000101

    dt = dt.replace(tzinfo=tz.gettz('UTC'))
    dt = dt.astimezone(tz.gettz('Europe/Madrid'))
    dt = dt.replace(tzinfo=None)
    if (dt - timedelta(seconds=(frame - 1) * exptime)).hour < 12:
        return datetime.strftime(dt - timedelta(days=1), '%Y%m%d')
    else:
        return (dt - timedelta(seconds=(frame - 1) * exptime)).strftime('%Y%m%d')
