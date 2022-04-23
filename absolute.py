from sys import path
from os import path as opath


def get_rp(file):
    return opath.dirname(opath.realpath(file))


rp = get_rp(__file__)


def pjoin(*args, **kwargs):
    return opath.join(*args, **kwargs)


def to_absolute(*args, **kwargs):
    return pjoin(rp, *args, **kwargs)


def add_imports(ipath=""):
    path.append(to_absolute(ipath))
