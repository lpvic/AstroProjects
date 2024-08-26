import os
from pathlib import Path
import shutil


def cp(src: Path, dst: Path) -> None:
    __file_operation(src, dst, shutil.copy2)


def mv(src: Path, dst: Path) -> None:
    __file_operation(src, dst, shutil.move)


def copy_dir(src: Path, dst: Path) -> None:
    fl = src.glob('*')
    for f in fl:
        if f.is_file():
            cp(f, dst / f.name)


def clean_dir(src: Path, prefix: str = '', ext: str = '') -> None:
    fl = src.glob('*')
    for f in fl:
        if f.is_file() & f.name.startswith(prefix) & f.name.endswith(ext):
            os.remove(f)


def renumber(filelist: list[Path], basename: str, startindex: int = 1) -> None:
    idx = startindex
    for f in filelist:
        mv(f, f.parent / (basename + '_{:0>5d}.' + f.suffix).format(idx))
        idx += 1


def get_file_list(srcdir: Path, basename: str) -> list[Path]:
    lst = []
    for f in os.listdir(srcdir):
        if f.startswith(basename) and f.endswith('.fit'):
            lst.append(srcdir / f)

    return lst


def get_list_dir(srcdir: str, prefix: str = '', ext: str = '') -> list[str]:
    file_list = []
    for file in os.listdir(srcdir):
        if file.endswith(ext) & file.startswith(prefix):
            file_list.append(file)
    return file_list


def __file_operation(src: Path, dst: Path, operation: callable):
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
