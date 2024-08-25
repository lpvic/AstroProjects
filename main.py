from pathlib import Path
from src.asiair_import import initialize_folders, read_asiair_files, update_metadata, import_files
from src.calibration_files import create_all_sequences

astroprojects_folder = Path(r'D:\AstroProjects')
asiar_root_folder = Path(r'D:\Asiair')
sources_paths = {'dark': astroprojects_folder / r'sources/darks', 'flat': astroprojects_folder / r'sources/flats',
                 'light': astroprojects_folder / r'sources/lights'}

# initialize_folders(astroprojects_folder)
# read_asiair_files(asiar_root_folder, astroprojects_folder)
# update_metadata(astroprojects_folder)
# import_files(asiar_root_folder, astroprojects_folder)

create_all_sequences(astroprojects_folder / 'sources')
