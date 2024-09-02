import platform

from pathlib import Path

import pandas as pd

from src.asiair_import import read_asiair_files, update_metadata, import_files
from src.calibration_files import create_master_file
from src.folder_structure import FolderStructure
from src.utils.fits_utils import get_fields_from_fits
from src.database import db_stacked_fields, read_files_database, read_stats_database
from src.utils.gen_utils import update_dict
from src.stats import calculate_stats


if platform.system() == 'Linux':
    astroprojects_folder = FolderStructure(r'/nas/sdm1/AstroProjects')
    asiar_root_folder = Path(r'/nas/sdm1/Asiair')
elif platform.system() == 'Windows':
    astroprojects_folder = FolderStructure(r'D:\AstroProjects')
    asiar_root_folder = Path(r'D:\Asiair')
else:
    exit(1)

# print('Creating ASIAir Database...')
# read_asiair_files(asiar_root_folder, astroprojects_folder)
# print('Updating Metadata...')
# update_metadata(astroprojects_folder)
# print('Calculating Statistics...')
#
# print('Importing Source Files...')
# import_files(asiar_root_folder, astroprojects_folder)
#
print('Creating Master Darks...')
for folder in [x for x in list(astroprojects_folder.sources_dict['dark'].rglob('*')) if x.is_dir()]:
    print('Processing {}...'.format(str(folder)))
    create_master_file(folder, astroprojects_folder)

print('Creating Master Flats...')
for folder in [x for x in list(astroprojects_folder.sources_dict['flat'].rglob('*')) if x.is_dir()]:
    print('Processing {}...'.format(str(folder)))
    create_master_file(folder, astroprojects_folder)

print('Creating Master Database...')
master_db_path = astroprojects_folder.metadata / 'master_database.csv'
if master_db_path.exists():
    master_db = read_files_database(master_db_path)
else:
    master_db = pd.DataFrame(columns=db_stacked_fields)

for file in list(astroprojects_folder.masters.rglob('master*.fit')):
    print('Processing {}...'.format(file))
    rel_file = file.relative_to(astroprojects_folder.root)
    if (rel_file in master_db['FILE'].values) or file.stat().st_size == 0:
        continue
    tmp = {'FILE': str(rel_file)}
    data = update_dict(get_fields_from_fits(file, db_stacked_fields), tmp)
    if data['IMAGETYP'] == 'dark':
        data['FILTER'] = ''
    master_db = pd.DataFrame(data, index=[0]) if master_db.empty \
        else pd.concat([master_db, pd.DataFrame(data, index=[0])])
    master_db.to_csv(master_db_path, sep=';', index=None)

print('Creating Statistics Database...')
stats_db_path = astroprojects_folder.metadata / 'stats.csv'
if stats_db_path.exists():
    stats_db = read_stats_database(stats_db_path)
else:
    stats_db = pd.DataFrame(columns=db_stacked_fields)
count = 1
files_list = list(astroprojects_folder.root.rglob('*.fit'))
total = len(files_list)
for file in files_list:
    rel_file = file.relative_to(astroprojects_folder.root)
    print('Processing {}% {} ({}/{})'.format(round(100 * count / total, 2), rel_file, count, total))
    count = count + 1
    if (rel_file in stats_db['FILE'].values) or file.stat().st_size == 0:
        continue
    tmp = {'FILE': str(rel_file)}
    file_stats = calculate_stats(file)
    for c in range(len(file_stats)):
        data = update_dict(tmp, file_stats[c])
        stats_db = pd.DataFrame(data, index=[0]) if stats_db.empty \
            else pd.concat([stats_db, pd.DataFrame(data, index=[0])])
        stats_db.to_csv(stats_db_path, sep=';', index=None)

print('Done.')
