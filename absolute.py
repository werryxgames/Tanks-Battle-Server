import sys
from os import path, mkdir
from shutil import copytree, copy


def get_rp(file):
    return path.dirname(path.realpath(file))


rp = get_rp(__file__)


def pjoin(*args, **kwargs):
    return path.join(*args, **kwargs)


def to_absolute(*args, temp=False, **kwargs):
    orig_path = pjoin(rp, *args, **kwargs)

    if hasattr(sys, "_MEIPASS"):
        if temp:
            return orig_path

        abs_home = path.abspath(path.expanduser("~"))
        abs_dir = path.join(abs_home, ".TBServer")

        if not path.exists(abs_dir):
            mkdir(abs_dir)

        abs_path = path.join(abs_dir, *args)

        if not path.exists(abs_path) and path.exists(orig_path):
            if path.isdir(orig_path):
                copytree(orig_path, abs_path)
            else:
                copy(orig_path, abs_path)
    else:
        abs_path = orig_path

    return abs_path


def add_imports(ipath=""):
    sys.path.append(to_absolute(ipath))
