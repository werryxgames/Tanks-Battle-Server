"""Модуль управления относительным путём."""
import sys

from os import mkdir
from os import path
from shutil import copy
from shutil import copytree

VERSION = "1.4.1"


def get_rp(file):
    """Возвращает абсолютный путь к файлу."""
    return path.dirname(path.realpath(file))


rp = get_rp(__file__)


def pjoin(*args, **kwargs):
    """Возвращает абсолютный путь из относительного."""
    return path.join(*args, **kwargs)


def to_absolute(*args, temp=False, **kwargs):
    """Превращает относительный путь в асболютный.

    Если не задан temp, в исполняемом файле, то будет сохранять данные.
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
    """Добавляет путь импортов."""
    sys.path.append(to_absolute(ipath))
