from pathlib import Path
import subprocess

from src.exceptions import NoSuitableDarkAvailable
from src.fits_utils import get_fields_from_foldername, get_raw_foldername, get_fields_from_fits, update_fits_fields
from src.database import db_raw_fields
from src.io_utils import cp
from src.folder_structure import FolderStructure


def get_nearest_exposure(value: float, exposures: set) -> float:
    min_diff = 1000000.
    out = None
    for exp in exposures:
        diff = abs(value - exp)
        if diff < min_diff:
            min_diff = diff
            out = exp
    return out


def get_nearest_session(value: int, sessions: set) -> int:
    min_diff = 1000000.
    out = None
    for ses in sessions:
        diff = abs(value - ses)
        if diff < min_diff:
            min_diff = diff
            out = ses
    return out


def select_master_dark(folders: FolderStructure, params: dict) -> Path:
    darks_list = folders.master_darks.glob('master_*.fit')
    reduced_list = []
    for dark in darks_list:
        dark_params = get_fields_from_fits(dark, db_raw_fields)
        if ((dark_params['XBINNING'] == params['XBINNING']) and
                (dark_params['INSTRUME'] == params['INSTRUME']) and
                (dark_params['GAIN'] == params['GAIN']) and
                (dark_params['SET-TEMP'] == params['SET-TEMP'])):
            reduced_list.append(dark_params)

    if not reduced_list:
        raise NoSuitableDarkAvailable(params)

    exp_set = {x['EXPTIME'] for x in reduced_list}
    nearest_exp = get_nearest_exposure(params['EXPTIME'], exp_set)
    reduced_list = [x for x in reduced_list if x['EXPTIME'] == nearest_exp]
    if len(reduced_list) > 1:
        ses_set = {x['SESSION'] for x in reduced_list}
        nearest_ses = get_nearest_session(params['SESSION'], ses_set)
        reduced_list = [x for x in reduced_list if x['SESSION'] == nearest_ses]

    return folders.master_darks / ('master_' + get_raw_foldername(reduced_list[0]) + '.fit')


def create_sequence(folder_path: Path) -> str:
    file_list = list(folder_path.glob('*.fit'))
    if not file_list:
        return ''
    nb_files = len(file_list)
    with open(r'templates/sequence_template.seq', 'r') as f_seq_template:
        seq_template = f_seq_template.read()
    with open(folder_path / (folder_path.name + '_.seq'), 'w') as f_seq:
        seq_content = seq_template.replace('{{sequence_name}}', folder_path.name)
        seq_content = seq_content.replace('{{nb_images}}', str(nb_files))
        seq_content = seq_content.replace('{{nb_selected}}', str(nb_files))
        for f in file_list:
            seq_number = int(f.stem.split('_')[-1])
            seq_content = seq_content + 'I ' + str(seq_number) + ' 1\n'
        f_seq.write(seq_content)
    return folder_path.name


def create_all_sequences(from_folder: Path) -> None:
    folder_list = [x for x in list(from_folder.rglob('*')) if x.is_dir()]
    for folder in folder_list:
        create_sequence(folder)


def create_master_script(folder_path: Path, folders: FolderStructure, siril_version: str = '1.2.0') -> None:
    img_type = folder_path.name.split('_')[0].lower()
    if (img_type != 'dark') and (img_type != 'flat'):
        return

    with open(r'templates\create_master_' + img_type + '_template.ssf', 'r') as f_script_template:
        master_template = f_script_template.read()
    with open(folder_path / ('create_master_' + img_type + '.ssf'), 'w') as f_ssf:
        out_file = folders.masters_dict[img_type] / ('master_' + folder_path.name + '.fit')
        rel_out_path = out_file.relative_to(folder_path, walk_up=True)
        script_content = master_template.replace('{{siril_version}}', siril_version)
        script_content = script_content.replace('{{sequence}}', folder_path.name)
        script_content = script_content.replace('{{out_file}}', str(rel_out_path))
        if img_type == 'flat':
            master_dark = select_master_dark(folders, get_fields_from_foldername(folder_path))
            rel_master_dark = master_dark.relative_to(folder_path, walk_up=True)
            script_content = script_content.replace('{{master_bias}}', str(rel_master_dark))
        f_ssf.write(script_content)


def create_all_scripts(from_folder: Path) -> None:
    folder_list = [x for x in list(from_folder.rglob('*')) if x.is_dir()]
    for folder in folder_list:
        create_master_script(folder)


def create_master_file(folder: Path, folders: FolderStructure, siril_version: str = '1.2.0', force: bool = False,
                       clean: bool = True) -> None:
    img_type = folder.name.split('_')[0].lower()
    master_file = folders.masters_dict[img_type] / ('master_' + folder.name + '.fit')
    if ((img_type != 'dark') and (img_type != 'flat')) or (master_file.exists() and not force):
        return

    create_sequence(folder)
    try:
        create_master_script(folder, siril_version)
        files_list = list(folder.glob('*.fit'))
        nb_files = len(files_list)
        subprocess.run('siril-cli -d ' + str(folder) + ' -s ' + str(folder / ('create_master_' + img_type + '.ssf')))
        if nb_files == 1:
            cp(files_list[0].with_name('pp_' + files_list[0].name), master_file)
        update_fits_fields(master_file, get_fields_from_foldername(folder))
        if clean:
            for f in folder.glob('pp_*.fit'):
                f.unlink(missing_ok=True)
    except NoSuitableDarkAvailable:
        print('No dark for ' + str(folder.name))
        return
