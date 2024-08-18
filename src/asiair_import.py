import os

import pandas as pd


def is_fits(filename):
    return filename.endswith('.fit')


def read_darks(start_folder):
    os_walk = os.walk(start_folder)
    folders = [x[0] for x in os_walk]
    filename_list = [x[2] for x in os_walk]

    for folder, filenames in zip(folders, filename_list):
        for file in filenames:
            if is_fits(file):
                abs_file = os.path.join(folder, file)


def read_flats(start_folder):
    pass


if __name__ == '__main__':
    asiar_folder = os.path.normpath(r'\\Debian-standard-lxqt\16t\Asiair')


    read_flats(asiar_folder)

    folder_list = [x[0] for x in os_walk]
    file_list = [x[2] for x in os_walk]

    print(os.path.relpath(asiar_folder, folder_list[1]))
