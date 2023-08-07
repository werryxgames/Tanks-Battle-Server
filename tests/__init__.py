"""Module with tests for Tanks Battle Server."""
from os import path as path_
from sys import path

try:
    path.append(
        path_.normpath(
            path_.join(
                path_.dirname(
                    path_.realpath(
                        __file__
                    )
                ),
                "..",
                "src"
            )
        )
    )
except IndexError:
    pass
