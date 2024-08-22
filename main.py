import os

from src.asiair_import import initialize_folders, create_fits_import_list, import_fits, apply_corrections
from src.calibration_libraries import create_master_files

dest_folder = os.path.normpath(r'D:\AstroProjects')
asiar_folder = os.path.normpath(r'D:\Asiair')

# initialize_folders(dest_folder)
# create_fits_import_list(asiar_folder, dest_folder)
# import_fits(asiar_folder, dest_folder, 'asiair_imported_files.csv')
# apply_corrections(dest_folder, 'changes.csv')
#
# create_master_files(dest_folder, 'dark')
# create_master_files(dest_folder, 'flat')
