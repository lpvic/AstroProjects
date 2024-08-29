from pathlib import Path
from src.asiair_import import initialize_folders, read_asiair_files, update_metadata, import_files
from src.calibration_files import create_master_file
from src.folder_structure import FolderStructure

astroprojects_folder = FolderStructure(r'D:\AstroProjects')
asiar_root_folder = Path(r'D:\Asiair')

initialize_folders(astroprojects_folder)
read_asiair_files(asiar_root_folder, astroprojects_folder)
update_metadata(astroprojects_folder)
import_files(asiar_root_folder, astroprojects_folder)

for folder in [x for x in list(astroprojects_folder.sources_dict['dark'].rglob('*')) if x.is_dir()]:
    create_master_file(folder)

for folder in [x for x in list(astroprojects_folder.sources_dict['flat'].rglob('*')) if x.is_dir()]:
    create_master_file(folder)
