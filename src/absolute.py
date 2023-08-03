"""Module for relative and absolute pathes."""
import sys

from os import mkdir
from os import path
from shutil import copy
from shutil import copytree

VERSION = "1.4.1"


def get_rp(file):
    """Returns absolute path to file."""
    return path.dirname(path.realpath(file))


rp = get_rp(__file__)


def pjoin(*args, **kwargs):
    """Returns absolute path from relative."""
    return path.join(*args, **kwargs)


def to_absolute(*args, temp=False, **kwargs):
    """Makes relative path absolute.

    If temp is not set in executable file, it will save data.
    """
    orig_path = pjoin(rp, *args, **kwargs)

    if hasattr(sys, "_MEIPASS"):
        if temp:
            return orig_path

        abs_home = path.abspath(path.expanduser("~"))
        abs_dir = path.join(abs_home, f".TBServer_v.{VERSION}")

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
    """Adds imports path."""
    sys.path.append(to_absolute(ipath))
