import platform

from pathlib import Path
from src.asiair_import import read_asiair_files, update_metadata, import_files
from src.calibration_files import create_master_file
from src.folder_structure import FolderStructure
from src.utils.fits_utils import get_fields_from_fits
from src.database import db_stacked_fields
from src.utils.gen_utils import update_dict


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
# print('Creating Master Darks...')
# for folder in [x for x in list(astroprojects_folder.sources_dict['dark'].rglob('*')) if x.is_dir()]:
#     create_master_file(folder, astroprojects_folder)
#
# print('Creating Master Flats...')
# for folder in [x for x in list(astroprojects_folder.sources_dict['flat'].rglob('*')) if x.is_dir()]:
#     create_master_file(folder, astroprojects_folder)

print('Creating Master Database...')
master_db = []
for file in list(astroprojects_folder.masters.rglob('master*.fit')):
    tmp = {'FILE': str(file.relative_to(astroprojects_folder.root)), 'AUTHOR': 'Luis Pedro Vicente Matilla'}
    data = update_dict(get_fields_from_fits(file, db_stacked_fields), tmp)


    print(data)
print('Done.')
