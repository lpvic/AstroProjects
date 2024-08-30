import platform

from pathlib import Path
from src.asiair_import import read_asiair_files, update_metadata, import_files
from src.calibration_files import create_master_file
from src.folder_structure import FolderStructure


if platform.system() == 'Linux':
    astroprojects_folder = FolderStructure(r'/nas/sdm1/AstroProjects')
    asiar_root_folder = Path(r'/nas/sdm1/Asiair')
elif platform.system() == 'Windows':
    astroprojects_folder = FolderStructure(r'D:\AstroProjects')
    asiar_root_folder = Path(r'D:\Asiair')
else:
    exit(1)

print('Creating ASIAir Database...')
read_asiair_files(asiar_root_folder, astroprojects_folder)
print('Updating Metadata...')
update_metadata(astroprojects_folder)
print('Importing Source Files...')
import_files(asiar_root_folder, astroprojects_folder)

print('Creating Master Darks...')
for folder in [x for x in list(astroprojects_folder.sources_dict['dark'].rglob('*')) if x.is_dir()]:
    create_master_file(folder, astroprojects_folder)

print('Creating Master Flats...')
for folder in [x for x in list(astroprojects_folder.sources_dict['flat'].rglob('*')) if x.is_dir()]:
    create_master_file(folder, astroprojects_folder)

print('Done.')
