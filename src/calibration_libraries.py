import os

from ioutils import get_file_list


def create_master_files(from_folder: str, image_type: str, siril_version: str, darks_lib: str = ''):
    img_type_folder = {'Dark': r'Darks\sources', 'Flat': r'Flats\sources'}
    lib_root = os.path.join(from_folder, img_type_folder[image_type])
    lib_folders = [x[1] for x in os.walk(lib_root)][0]



    for folder in lib_folders:
        folder_path = os.path.join(lib_root, folder)
        file_list = get_file_list(folder_path, folder)
        nb_files = len(file_list)
        if nb_files > 1:
            with open(r'..\templates\sequence_template.seq', 'r') as f_seq_template:
                seq_template = f_seq_template.read()
            with open(os.path.join(folder_path, folder + '.seq'), 'w') as f_seq:
                seq_content = seq_template.replace('{{sequence_name}}', folder)
                seq_content = seq_content.replace('{{nb_images}}', str(nb_files))
                seq_content = seq_content.replace('{{nb_selected}}', str(nb_files))
                for f in file_list:
                    seq_number = int(f[:-4].split('_')[-1])
                    seq_content = seq_content + 'I ' + str(seq_number) + ' 1\n'
                f_seq.write(seq_content)
            with open(r'..\templates\create_master_' + image_type + '_template.ssf', 'r') as f_script_template:
                master_template = f_script_template.read()
            with open(os.path.join(folder_path, 'create_master' + image_type + '.ssf'), 'w') as f_ssf:
                script_content = master_template.replace('{{siril_version}}', siril_version)
                script_content = script_content.replace('{{sequence}}', folder)

    pass


if __name__ == '__main__':
    start_folder = os.path.normpath(r'D:\AstroProjects')

    create_master_files(start_folder, 'Dark', '1.2.0')
