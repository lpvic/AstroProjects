import os
import shutil


def mkdir(path):
    try:
        os.makedirs(path)
        return True
    except FileExistsError:
        return False


def copy_file(src, dst):
    __file_operation(src, dst, shutil.copy2)


def move_file(src, dst):
    __file_operation(src, dst, shutil.move)


def copy_dir(src, dst):
    fl = os.listdir(src)
    for f in fl:
        if os.path.isfile(os.path.join(src, f)):
            copy_file(os.path.join(src, f), os.path.join(dst, f))


def clean_dir(src, prefix='', ext=''):
    fl = os.listdir(src)
    for f in fl:
        file = os.path.join(src, f)
        if os.path.isfile(file) & f.startswith(prefix) & f.endswith(ext):
            os.remove(os.path.join(src, f))


def renumber(filelist, basename, startindex=1):
    idx = startindex
    for f in filelist:
        move_file(f, os.path.join(os.path.dirname(f), (basename + '_{:0>5d}.' + f.split('.')[-1]).format(idx)))
        idx += 1


def get_file_list(srcdir, basename):
    lst = []
    for f in os.listdir(srcdir):
        if f.startswith(basename) and f.endswith('.fit'):
            lst.append(os.path.join(srcdir, f))

    return lst


def get_list_dir(srcdir, prefix='', ext=''):
    file_list = []
    for file in os.listdir(srcdir):
        if file.endswith(ext) & file.startswith(prefix):
            file_list.append(file)
    return file_list


def __file_operation(src, dst, operation):
    if isinstance(src, list):
        if isinstance(dst, list):
            if len(src) == len(dst):
                for fin, fout in zip(src, dst):
                    operation(fin, fout)
            else:
                raise Exception('Source and destination Lists must have the same length')
        else:
            for fin in src:
                operation(fin, os.path.join(dst, os.path.basename(fin)))
    else:
        if os.path.isdir(dst):
            operation(src, os.path.join(dst, os.path.basename(src)))
        else:
            operation(src, dst)
