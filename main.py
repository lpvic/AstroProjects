from pathlib import Path
from src.asiair_import import initialize_folders, read_asiair_files, update_metadata, import_files
from src.calibration_files import create_master_file
from time import time

timing = [time()]
astroprojects_folder = Path(r'D:\AstroProjects')
asiar_root_folder = Path(r'D:\Asiair')
sources_paths = {'dark': astroprojects_folder / r'sources/darks', 'flat': astroprojects_folder / r'sources/flats',
                 'light': astroprojects_folder / r'sources/lights'}

timing.append(time())
initialize_folders(astroprojects_folder)
timing.append(time())
read_asiair_files(asiar_root_folder, astroprojects_folder)
timing.append(time())
update_metadata(astroprojects_folder)
timing.append(time())
import_files(asiar_root_folder, astroprojects_folder)

timing.append(time())
for folder in [x for x in list(sources_paths['dark'].rglob('*')) if x.is_dir()]:
    create_master_file(folder)

timing.append(time())
for folder in [x for x in list(sources_paths['flat'].rglob('*')) if x.is_dir()]:
    create_master_file(folder)
timing.append(time())

print(timing)
print([timing[i] - timing[i-1] for i in range(1, len(timing))])
