from pathlib import Path
from src.asiair_import import initialize_folders, read_asiair_files, update_metadata

astroprojects_folder = Path(r'D:\AstroProjects')
asiar_root_folder = Path(r'D:\Asiair')

initialize_folders(astroprojects_folder)
read_asiair_files(asiar_root_folder, astroprojects_folder)
update_metadata(astroprojects_folder)
