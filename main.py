from pathlib import Path
from src.asiair_import import initialize_folders, read_asiair_files, update_metadata, import_files
from src.calibration_files import create_sequence

astroprojects_folder = Path(r'D:\AstroProjects')
asiar_root_folder = Path(r'D:\Asiair')
sources_paths = {'dark': astroprojects_folder / r'sources/darks', 'flat': astroprojects_folder / r'sources/flats',
                 'light': astroprojects_folder / r'sources/lights'}

# initialize_folders(astroprojects_folder)
# read_asiair_files(asiar_root_folder, astroprojects_folder)
# update_metadata(astroprojects_folder)
# import_files(asiar_root_folder, astroprojects_folder)

# create_sequence(Path(r'D:\AstroProjects\sources\darks\Dark_20230729_04_180000.0ms_Bin1_294MC_Gain120_-10.0C'))
dir_list = [x for x in list(sources_paths['dark'].glob('*')) if x.is_dir()]
print(dir_list[0].stem)
