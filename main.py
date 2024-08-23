from pathlib import Path
from src.asiair_import import update_database

astroprojects_folder = Path(r'D:\AstroProjects')
asiar_root_folder = Path(r'D:\Asiair')

# initialize_folders(dest_folder)
# create_fits_import_list(asiar_folder, dest_folder)
# import_fits(asiar_folder, dest_folder, 'asiair_imported_files.csv')
# apply_corrections(dest_folder, 'changes.csv')
#
# create_master_files(dest_folder, 'dark')
# create_master_files(dest_folder, 'flat')

update_database(asiar_root_folder, astroprojects_folder, 'dark')