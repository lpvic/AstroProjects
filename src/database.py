db_raw_fields = ['ASIFILE', 'NEWFILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SEQUENCE', 'FRAME', 'INSTRUME', 'FILTER',
                 'EXPTIME', 'XBINNING', 'GAIN', 'SET-TEMP', 'GUIDECAM', 'MOUNT', 'TELESCOP', 'LENS', 'FOCALLEN',
                 'OBJECT', 'OBSERVER',  'SITENAME', 'SITELAT', 'SITELON']

db_stacked_fields = ['FILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SEQUENCE', 'INSTRUME', 'FILTER',
                     'EXPTIME', 'XBINNING', 'GAIN', 'SET-TEMP', 'GUIDECAM', 'MOUNT', 'TELESCOP', 'LENS', 'FOCALLEN',
                     'OBJECT', 'AUTHOR',  'SITENAME', 'SITELAT', 'SITELON']

db_raw_fields_type = {
    'dark': ['ASIFILE', 'NEWFILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SEQUENCE', 'FRAME', 'INSTRUME', 'EXPTIME',
             'XBINNING', 'GAIN', 'SET-TEMP', 'OBSERVER'],
    'flat': ['ASIFILE', 'NEWFILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SEQUENCE', 'FRAME', 'INSTRUME', 'FILTER',
             'EXPTIME', 'XBINNING', 'GAIN', 'SET-TEMP', 'TELESCOP', 'LENS', 'FOCALLEN', 'OBSERVER'],
    'light': ['ASIFILE', 'NEWFILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SEQUENCE', 'FRAME', 'INSTRUME', 'FILTER',
              'EXPTIME', 'XBINNING', 'GAIN', 'SET-TEMP', 'GUIDECAM', 'MOUNT', 'TELESCOP', 'LENS', 'FOCALLEN',
              'OBJECT', 'OBSERVER',  'SITENAME', 'SITELAT', 'SITELON']
}

db_stacked_fields_type = {
    'master_dark': ['FILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SEQUENCE', 'INSTRUME', 'EXPTIME', 'XBINNING', 'GAIN',
                    'SET-TEMP', 'AUTHOR'],
    'master_flat': ['FILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SEQUENCE', 'INSTRUME', 'FILTER',
                    'EXPTIME', 'XBINNING', 'GAIN', 'SET-TEMP', 'TELESCOP', 'LENS', 'FOCALLEN', 'AUTHOR'],
    'stacked': ['FILE', 'IMAGETYP', 'DATE-OBS', 'SESSION', 'SEQUENCE', 'INSTRUME', 'FILTER',
                'EXPTIME', 'XBINNING', 'GAIN', 'SET-TEMP', 'GUIDECAM', 'MOUNT', 'TELESCOP', 'LENS', 'FOCALLEN',
                'OBJECT', 'AUTHOR',  'SITENAME', 'SITELAT', 'SITELON']
}

