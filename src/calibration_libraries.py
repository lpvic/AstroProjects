import os
import subprocess

from ioutils import get_file_list, get_list_dir, clean_dir, copy_file
from asiair_import import get_fields_from_foldername, create_foldername
from exceptions import NoSuitableDarkAvailable


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


def select_master_dark(from_folder: str, params: dict) -> str:
    src_darks = os.path.join(from_folder, r'masters\darks')
    darks_list = get_list_dir(src_darks, prefix='master', ext='fit')
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

    return os.path.join(src_darks, 'master_' + create_foldername(reduced_list[0]) + '.fit')


def create_master_files(from_folder: str, image_type: str, siril_version: str = '1.2.0', force: bool = False,
                        clean: bool = True) -> None:
    image_type = image_type.lower()

    img_type_folder = {'dark': r'sources\darks', 'flat': r'sources\flats'}
    src_root = os.path.join(from_folder, img_type_folder[image_type])
    src_folders = [x[1] for x in os.walk(src_root)][0]
    out_root = {'dark': r'masters\darks', 'flat': r'masters\flats'}

    for folder in src_folders:
        folder_path = os.path.join(src_root, folder)
        file_list = get_file_list(folder_path, folder)
        nb_files = len(file_list)
        if (os.path.exists(os.path.join(from_folder, out_root[image_type], 'master_' + folder + '.fit')) and
                not force):
            continue

        with open(r'..\templates\sequence_template.seq', 'r') as f_seq_template:
            seq_template = f_seq_template.read()
        with open(os.path.join(folder_path, folder + '_.seq'), 'w') as f_seq:
            seq_content = seq_template.replace('{{sequence_name}}', folder)
            seq_content = seq_content.replace('{{nb_images}}', str(nb_files))
            seq_content = seq_content.replace('{{nb_selected}}', str(nb_files))
            for f in file_list:
                seq_number = int(f[:-4].split('_')[-1])
                seq_content = seq_content + 'I ' + str(seq_number) + ' 1\n'
            f_seq.write(seq_content)

        if nb_files > 1:
            with open(r'..\templates\create_master_' + image_type + '_template.ssf', 'r') as f_script_template:
                master_template = f_script_template.read()
            with open(os.path.join(folder_path, 'create_master_' + image_type + '.ssf'), 'w') as f_ssf:
                out_file = os.path.join(from_folder, out_root[image_type], 'master_' + folder + '.fit')
                rel_out_path = os.path.relpath(out_file, os.path.join(src_root, folder))
                script_content = master_template.replace('{{siril_version}}', siril_version)
                script_content = script_content.replace('{{sequence}}', folder)
                script_content = script_content.replace('{{out_file}}', rel_out_path)
                if image_type == 'flat':
                    try:
                        master_dark = select_master_dark(from_folder, get_fields_from_foldername(folder))
                    except NoSuitableDarkAvailable:
                        continue
                    rel_master_dark = os.path.relpath(master_dark, os.path.join(src_root, folder))
                    script_content = script_content.replace('{{master_bias}}', rel_master_dark)
                f_ssf.write(script_content)

            subprocess.run('siril-cli -d ' + folder_path + ' -s ' +
                           os.path.join(folder_path, 'create_master_' + image_type + '.ssf'))
        elif nb_files == 1:
            if image_type == 'darks':
                in_file = os.path.join(folder_path, file_list[0])
                out_file = os.path.join(from_folder, out_root[image_type], 'master_' + folder + '.fit')
                with open(r'..\templates\sequence_stats_template.ssf', 'r') as f_script_template:
                    master_template = f_script_template.read()
                with open(os.path.join(folder_path, 'sequence_stats.ssf'), 'w') as f_ssf:
                    script_content = master_template.replace('{{siril_version}}', siril_version)
                    script_content = script_content.replace('{{sequence}}', folder)
                    f_ssf.write(script_content)
                subprocess.run('siril-cli -d ' + folder_path + ' -s ' +
                               os.path.join(folder_path, 'sequence_stats.ssf'))
                copy_file(in_file, out_file)
            elif image_type == 'flats':
                in_file = os.path.join(folder_path, 'pp_' + file_list[0])
                out_file = os.path.join(from_folder, out_root[image_type], 'master_' + folder + '.fit')
                with open(r'..\templates\calibrate_single_file_template.ssf', 'r') as f_script_template:
                    master_template = f_script_template.read()
                with open(os.path.join(folder_path, 'create_master_' + image_type + '_.ssf'), 'w') as f_ssf:
                    script_content = master_template.replace('{{siril_version}}', siril_version)
                    script_content = script_content.replace('{{image}}', file_list[0])
                    script_content = script_content.replace('{{sequence}}', folder)
                    try:
                        master_dark = select_master_dark(from_folder, get_fields_from_foldername(folder))
                    except NoSuitableDarkAvailable:
                        continue
                    rel_master_dark = os.path.relpath(master_dark, os.path.join(src_root, folder))
                    script_content = script_content.replace('{{master_bias}}', rel_master_dark)
                    f_ssf.write(script_content)
                subprocess.run('siril-cli -d ' + folder_path + ' -s ' +
                               os.path.join(folder_path, 'create_master_' + image_type + '.ssf'))

                copy_file(in_file, out_file)
            else:
                continue

        # TODO: standardize stats files

        if clean:
            clean_dir(folder_path, prefix='pp_', ext='.fit')

    # TODO: obtain stats for master files

    # TODO: compile all stats


if __name__ == '__main__':
    start_folder = os.path.normpath(r'D:\AstroProjects')

    create_master_files(start_folder, 'dark')
    create_master_files(start_folder, 'flat')
