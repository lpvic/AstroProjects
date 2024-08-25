from pathlib import Path

from src.exceptions import NoSuitableDarkAvailable
from src.fits_utils import get_fields_from_foldername, get_foldername


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


def select_master_dark(from_folder: Path, params: dict) -> Path:
    src_darks = from_folder / r'masters\darks'
    darks_list = src_darks.glob('master_*.fit')
    reduced_list = []
    for dark in darks_list:
        dark_params = get_fields_from_foldername(dark[7:-4])
        if ((dark_params['XBINNING'] == params['XBINNING']) and
                (dark_params['INSTRUME'] == params['INSTRUME']) and
                (dark_params['GAIN'] == params['GAIN']) and
                (dark_params['SET-TEMP'] == params['SET-TEMP'])):
            reduced_list.append(dark_params)

    if not reduced_list:
        raise NoSuitableDarkAvailable(params)

    exp_set = {x['EXPOSURE'] for x in reduced_list}
    nearest_exp = get_nearest_exposure(params['EXPOSURE'], exp_set)
    reduced_list = [x for x in reduced_list if x['EXPOSURE'] == nearest_exp]
    if len(reduced_list) > 1:
        ses_set = {x['SESSION'] for x in reduced_list}
        nearest_ses = get_nearest_session(params['SESSION'], ses_set)
        reduced_list = [x for x in reduced_list if x['SESSION'] == nearest_ses]

    return src_darks / ('master_' + get_foldername(reduced_list[0]) + '.fit')


def create_sequence(folder_path: Path) -> str:
    file_list = list(folder_path.glob('*.fit'))
    if not file_list:
        return ''
    nb_files = len(file_list)
    with open(r'templates/sequence_template.seq', 'r') as f_seq_template:
        seq_template = f_seq_template.read()
    with open(folder_path / (folder_path.name + '.seq'), 'w') as f_seq:
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


def create_master_file(from_folder: Path, siril_version: str = '1.2.0', force: bool = False, clean: bool = True)\
        -> None:
    pass
